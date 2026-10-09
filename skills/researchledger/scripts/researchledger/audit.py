"""Deterministic evidence/deviation checks; scientific validity requires review."""
import fnmatch
import json
import statistics

from . import schema
from .store import LedgerError, canonical, record


def inspect_run(ledger, run):
    exp = ledger.get(run["experiment_id"], "experiment")
    c = exp["contract"]
    deviations, unknown, drift = [], [], []
    report = run.get("report")
    refs = list(run["inputs"].values()) + [run["config_artifact"]]
    for rid in run.get("evidence", []):
        try:
            refs.append(ledger.get(rid, "evidence")["artifact"])
        except LedgerError as exc:
            unknown.append(str(exc))
    for ref in refs:
        try:
            ledger.store.read_blob(ref)
        except LedgerError as exc:
            unknown.append(str(exc))
    if run.get("status") != "Finished":
        unknown.append("Execution interrupted; no finish receipt")
    if run.get("error"):
        unknown.append(run["error"])
    for path in run.get("changes", []):
        if path == "Unknown":
            unknown.append("Post-run workspace unknown")
        elif any(fnmatch.fnmatchcase(path, p) for p in c["forbidden_changes"]) or not any(fnmatch.fnmatchcase(path, p) for p in c["allowed_changes"]):
            deviations.append("Unauthorized file change: " + path)
    for key in ("model", "dataset", "algorithm", "metric", "seeds"):
        if key not in run["config"]:
            unknown.append("Config missing " + key)
        elif run["config"][key] != c[key]:
            deviations.append("Contract/config mismatch: " + key)
    for key, expected in exp["invariants"].items():
        if key not in run["config"]:
            unknown.append("Innovation invariant unobserved: " + key)
        elif run["config"][key] != expected:
            drift.append("Innovation invariant changed: " + key)
    values = {}
    try:
        schema.fields(report, ("observed", "trials"))
        observed = report["observed"]
        schema.require(isinstance(observed, dict), "observed must be object")
        for key in ("model", "dataset", "algorithm", "metric", "seeds"):
            if key not in observed:
                unknown.append("Report missing observed " + key)
            elif observed[key] != c[key]:
                deviations.append("Contract/report mismatch: " + key)
        for key, expected in exp["invariants"].items():
            if key not in observed:
                unknown.append("Reported mechanism unknown: " + key)
            elif observed[key] != expected:
                drift.append("Reported innovation drift: " + key)
        schema.require(isinstance(report["trials"], list) and report["trials"], "No trial evidence")
        for trial in report["trials"]:
            schema.fields(trial, ("seed", "variant", "value", "model", "dataset", "metric", "evaluation", "compute_budget"))
            schema.require(type(trial["seed"]) is int and trial["seed"] in c["seeds"], "Unexpected trial seed")
            schema.require(trial["variant"] in ("baseline", "treatment"), "Invalid trial variant")
            schema.number(trial["value"], "metric value")
            schema.number(trial["compute_budget"], "compute_budget", True)
            key = (trial["seed"], trial["variant"])
            schema.require(key not in values, "Duplicate trial")
            values[key] = trial
            for name in ("model", "dataset", "metric", "evaluation"):
                if trial[name] != c[name]:
                    deviations.append("Unfair/changed " + name + " in " + str(key))
        for seed in c["seeds"]:
            b, t = values.get((seed, "baseline")), values.get((seed, "treatment"))
            if not b or not t:
                unknown.append("Missing paired seed: " + str(seed))
            elif b["compute_budget"] != t["compute_budget"]:
                deviations.append("Unequal compute budget for seed " + str(seed))
    except (LedgerError, TypeError, KeyError) as exc:
        unknown.append("Invalid report: " + str(exc))
    deltas = [values[(s, "treatment")]["value"] - values[(s, "baseline")]["value"] for s in c["seeds"]
              if (s, "treatment") in values and (s, "baseline") in values]
    delta = statistics.mean(deltas) if deltas else None
    signed = delta if c["acceptance"]["direction"] == "maximize" else (-delta if delta is not None else None)
    improved = signed is not None and signed > 0
    accepted = signed is not None and signed >= c["acceptance"]["min_delta"] and len(deltas) >= c["acceptance"]["min_pairs"]
    # A detected boundary violation takes precedence; execution success remains a separate fact.
    success = run.get("exit_code") == 0 and not run.get("stopped") and run.get("status") == "Finished"
    status = "Deviated" if deviations or drift else ("Failed" if run.get("exit_code") not in (None, 0) or run.get("stopped") else ("Unverified" if unknown or not success else "Completed"))
    return {"experiment_id": exp["id"], "run_id": run["id"], "status": status, "execution_success": success,
            "metric_improved": improved, "acceptance_met": accepted, "mean_delta": delta, "paired_seeds": len(deltas),
            "deviations": sorted(set(deviations)), "unknown": sorted(set(unknown)), "drift": sorted(set(drift)),
            "hypothesis_support": "Pending researcher review", "reproducibility": "Captured inputs and paired seed report; independent rerun Unknown",
            "limitations": ["Observed configuration and metrics are process-reported; semantic mechanism, data leakage and external effects require review.",
                            "Function extraction proves source presence, not that each function executed."]}


def method_card(ledger, run, audit):
    exp = ledger.get(run["experiment_id"], "experiment")
    c = exp["contract"]
    # Use the pinned historical innovation, not its potentially revised current text.
    inv = next(r for r in ledger.history(exp["innovation_id"], "innovation", 1000000) if r["id"] == exp["innovation_id"] and r["version"] == exp["innovation_version"])
    return {"experiment_id": exp["id"], "run_id": run["id"], "motivation": inv["motivation"], "principle": inv["mechanism"],
            "declared_algorithm": c["algorithm"], "captured_config": run["config"], "core_functions": run["functions"], "code_artifacts": run["inputs"],
            "git_commit": run["git_commit"], "git_status": run["git_status"], "environment": run["environment"], "command": run["command"],
            "execution_flow": "Runner receipt -> captured source/config -> process -> raw log/result -> paired comparison",
            "runtime_call_trace": "Unknown", "dependency_lock": "Captured only when explicitly listed in contract.code; otherwise Unknown",
            "changes": run.get("changes", "Unknown"), "data_processing_declared": c["data_processing"], "training_declared": c["training"], "evaluation_declared": c["evaluation"],
            "results": {k: audit[k] for k in ("status", "execution_success", "metric_improved", "acceptance_met", "mean_delta", "unknown", "drift")},
            "evidence": run.get("evidence", []), "scientific_validity": "Unknown until researcher review; declarations are not execution proof"}


def persist_audit(ledger, run, locked=False):
    def commit():
        result = inspect_run(ledger, run)
        exp = ledger.get(run["experiment_id"], "experiment")
        audit = record("audit", dict(result, evidence=run.get("evidence", [])), "auditor")
        card = record("method", method_card(ledger, run, result), "auditor")
        ledger.save([audit, card, record("experiment", dict(exp, status=result["status"], evidence=exp["evidence"] + [audit["id"], card["id"]]), "auditor", exp)], "audit", "auditor")
        return audit
    if locked:
        return commit()
    with ledger.store.lock():
        return commit()


def audit(ledger, experiment_id, save=False):
    runs = [r for r in ledger.store.records().values() if r["kind"] == "run" and r["experiment_id"] == experiment_id]
    schema.require(runs, "No run to audit")
    return persist_audit(ledger, runs[-1]) if save else inspect_run(ledger, runs[-1])
