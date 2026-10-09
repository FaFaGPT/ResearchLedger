"""Scientific state transitions. All public mutations serialize on the ledger lock."""
import copy
import fnmatch
import json
from collections import Counter

from . import schema
from .store import Store, LedgerError, atomic_write, canonical, confined, digest, record


class Ledger:
    def __init__(self, root):
        self.store = Store(root)

    def get(self, rid, kind=None):
        result = self.store.records().get(rid)
        schema.require(result is not None and (not kind or result["kind"] == kind), "Unknown %s: %s" % (kind or "record", rid))
        return result

    def goal(self):
        goals = [r for r in self.store.records().values() if r["kind"] == "goal"]
        schema.require(len(goals) == 1, "Initialize a research goal first")
        return goals[0]

    def save(self, records, action, source):
        self.store.append(records, action, source)
        state = self.status()
        atomic_write(confined(self.store.home, "state.json"), (canonical(state) + "\n").encode())
        atomic_write(confined(self.store.home, "STATE.md"), self.resume().encode())

    def init(self, title, source="researcher"):
        schema.text(title, "goal")
        with self.store.lock(create=True):
            schema.require(not self.store.events(), "Ledger already initialized")
            goal = record("goal", {"title": title, "mode": "Strict", "primary_innovation": None, "exploration": None}, source)
            self.save([goal], "init", source)
        return goal

    def add_innovation(self, data, source="researcher"):
        schema.innovation(data)
        with self.store.lock():
            self.goal()
            if source != "researcher":
                schema.require(data["origin"] == "AI-Proposed", "Agent ideas must be AI-Proposed")
            for rid in data.get("literature", []):
                self.get(rid, "literature")
            r = record("innovation", dict(data, status="Candidate", assessment="Untested", relations=[]), source)
            self.save([r], "innovation.add", source)
        return r

    def evolve(self, rid, action, reason, source="researcher", data=None, targets=None):
        schema.text(reason, "reason")
        schema.require(source == "researcher", "Innovation direction changes require researcher authorization")
        with self.store.lock():
            old = self.get(rid, "innovation")
            values = copy.deepcopy(old)
            statuses = {"approve": "Active", "pause": "Paused", "reject": "Rejected", "replace": "Superseded", "split": "Split", "revise": "Candidate"}
            schema.require(action in statuses, "Invalid evolution action")
            if action == "revise":
                schema.innovation(data)
                values.update(data)
                values["assessment"] = "Untested"
            if action in ("replace", "split"):
                schema.require(bool(targets) and (action != "split" or len(targets) >= 2), "Evolution requires target innovations")
                schema.require(rid not in targets and len(set(targets)) == len(targets), "Invalid evolution targets")
                for target in targets:
                    self.get(target, "innovation")
            values["status"] = statuses[action]
            values["relations"].append({"action": action, "targets": targets or [], "reason": reason, "from_version": old["version"]})
            r = record("innovation", values, source, old)
            changes = [r]
            goal = self.goal()
            if action == "approve" and not goal["primary_innovation"]:
                changes.append(record("goal", dict(goal, primary_innovation=rid), source, goal))
            self.save(changes, "innovation." + action, source)
        return r

    def set_primary(self, rid, reason, source="researcher"):
        schema.require(source == "researcher", "Primary direction requires researcher authorization")
        schema.text(reason, "reason")
        with self.store.lock():
            innovation = self.get(rid, "innovation")
            schema.require(innovation["status"] == "Active", "Primary innovation must be Active")
            goal = self.goal()
            decision = record("decision", {"target": rid, "outcome": "primary-direction", "reason": reason}, source)
            self.save([record("goal", dict(goal, primary_innovation=rid), source, goal), decision], "primary", source)
        return decision

    def policy(self, mode, exploration=None, source="researcher"):
        schema.require(source == "researcher", "Policy changes require researcher authorization")
        schema.require(mode in ("Strict", "Bounded", "Explore"), "Invalid policy mode")
        with self.store.lock():
            goal = self.goal()
            if mode == "Explore":
                schema.fields(exploration, ("innovations", "allowed_changes", "max_runs", "max_total_seconds", "branch_prefix"))
                schema.strings(exploration["innovations"], "innovations")
                for rid in exploration["innovations"]:
                    self.get(rid, "innovation")
                schema.strings(exploration["allowed_changes"], "allowed_changes", False)
                for path in exploration["allowed_changes"]:
                    from .store import relative
                    relative(path)
                schema.require(type(exploration["max_runs"]) is int and exploration["max_runs"] > 0, "max_runs must be positive")
                schema.number(exploration["max_total_seconds"], "max_total_seconds", True)
                schema.require(exploration["branch_prefix"].startswith("explore/") and len(exploration["branch_prefix"]) > 8, "Use an explicit explore/<namespace>/ branch prefix")
            r = record("goal", dict(goal, mode=mode, exploration=exploration if mode == "Explore" else None), source, goal)
            self.save([r], "policy", source)
        return r

    def plan(self, data, source="agent"):
        schema.contract(data)
        with self.store.lock():
            inv = self.get(data["innovation_id"], "innovation")
            schema.require(inv["status"] not in ("Rejected", "Superseded", "Split", "Paused"), "Innovation is not executable")
            # Duplicate identity excludes prose but includes execution-relevant settings and current input bytes.
            inputs = {}
            for name in [data["config"]] + data["code"]:
                path = confined(self.store.root, name)
                schema.require(path.is_file(), "Missing input: " + name)
                schema.require(path.stat().st_size <= 16 * 1024 * 1024, "Input too large for V1; use a manifest")
                inputs[name] = self.store.blob(path.read_bytes())
            keys = ("innovation_id", "algorithm", "model", "dataset", "metric", "seeds", "command", "evaluation", "acceptance", "budget")
            fingerprint = digest(canonical({"contract": {k: data[k] for k in keys}, "inputs": inputs}).encode())
            duplicates = [r["id"] for r in self.store.records().values() if r["kind"] == "experiment" and r["fingerprint"] == fingerprint]
            if duplicates:
                schema.require(data.get("replication_of") in duplicates and bool(data.get("replication_reason")), "Duplicate experiment: " + ", ".join(duplicates) + "; declare replication_of and replication_reason")
            elif data.get("replication_of"):
                self.get(data["replication_of"], "experiment")
                schema.text(data.get("replication_reason"), "replication_reason")
            hypothesis = record("hypothesis", {"innovation_id": inv["id"], "statement": data["hypothesis"], "status": "Untested"}, source)
            exp = record("experiment", {"title": data["title"], "contract": data, "innovation_id": inv["id"], "innovation_version": inv["version"],
                                        "invariants": inv["invariants"], "hypothesis_id": hypothesis["id"], "hypothesis_version": hypothesis["version"],
                                        "fingerprint": fingerprint, "inputs": inputs, "status": "Planned", "approval": None}, source)
            self.save([hypothesis, exp], "plan", source)
        return exp

    def approve(self, rid, reason, source="researcher"):
        schema.require(source == "researcher", "Execution approval requires researcher authorization")
        schema.text(reason, "approval reason")
        with self.store.lock():
            exp = self.get(rid, "experiment")
            schema.require(exp["status"] == "Planned", "Only planned contracts can be approved")
            inv = self.get(exp["innovation_id"], "innovation")
            schema.require(inv["status"] == "Active" and inv["version"] == exp["innovation_version"], "Innovation changed or is not Active; create a new contract")
            approved = record("experiment", dict(exp, approval={"source": source, "reason": reason, "fingerprint": exp["fingerprint"]}), source, exp)
            self.save([approved], "approve", source)
        return approved

    def checkpoint(self, current_task, next_steps, unresolved, source="agent"):
        schema.text(current_task, "current_task")
        schema.strings(next_steps, "next_steps", False)
        schema.strings(unresolved, "unresolved", False)
        with self.store.lock():
            self.goal()
            old = next((r for r in self.store.records().values() if r["kind"] == "memory"), None)
            r = record("memory", {"current_task": current_task, "next_steps": next_steps, "unresolved": unresolved}, source, old)
            self.save([r], "checkpoint", source)
        return r

    def literature(self, title, locator, innovations=None, source="researcher"):
        schema.text(title, "title")
        schema.text(locator, "locator")
        with self.store.lock():
            self.goal()
            for rid in innovations or []:
                self.get(rid, "innovation")
            r = record("literature", {"title": title, "locator": locator, "innovations": innovations or []}, source)
            self.save([r], "literature", source)
        return r

    def decision(self, experiment_id, outcome, reason, review_path, source="researcher"):
        schema.require(source == "researcher", "Scientific decisions require researcher authorization")
        schema.require(outcome in ("Supported", "Refuted", "Inconclusive"), "Invalid outcome")
        schema.text(reason, "reason")
        with self.store.lock():
            exp = self.get(experiment_id, "experiment")
            audits = [r for r in self.store.records().values() if r["kind"] == "audit" and r["experiment_id"] == experiment_id]
            schema.require(audits, "Audit required")
            latest = audits[-1]
            if outcome != "Inconclusive":
                schema.require(latest["status"] == "Completed" and not exp["contract"].get("exploratory", False), "Only verified confirmatory experiments can support formal conclusions")
                # Re-audit blob integrity at the point of promotion.
                from .audit import inspect_run
                fresh = inspect_run(self, self.get(latest["run_id"], "run"))
                schema.require(fresh["status"] == "Completed", "Evidence is no longer verified")
                if outcome == "Supported":
                    schema.require(fresh["acceptance_met"], "Acceptance criteria were not met")
            review = confined(self.store.root, review_path)
            schema.require(review.is_file() and review.stat().st_size <= 1024 * 1024, "Review must be a local file of at most 1 MiB")
            raw = review.read_bytes()
            schema.require(bool(raw.strip()), "Empty scientific review")
            evidence = record("evidence", {"experiment_id": experiment_id, "type": "researcher-review", "artifact": self.store.blob(raw), "original_path": review_path}, source)
            decision = record("decision", {"target": experiment_id, "innovation_id": exp["innovation_id"], "hypothesis_id": exp["hypothesis_id"], "outcome": outcome, "reason": reason,
                                           "evidence": [latest["id"], evidence["id"]]}, source)
            hyp = self.get(exp["hypothesis_id"], "hypothesis")
            inv = self.get(exp["innovation_id"], "innovation")
            schema.require(inv["version"] == exp["innovation_version"], "Innovation changed; evaluate evidence against a current contract")
            # Assessment revisions do not invalidate mechanism pins: keep assessments on hypotheses/decisions.
            self.save([evidence, decision, record("hypothesis", dict(hyp, status=outcome, evidence=hyp["evidence"] + [decision["id"]]), source, hyp)], "decision", source)
        return decision

    def status(self, limit=8):
        records = list(self.store.records().values())
        goals = [r for r in records if r["kind"] == "goal"]
        schema.require(goals, "No research ledger initialized")
        goal = goals[0]
        experiments = [r for r in records if r["kind"] == "experiment"]
        memory = next((r for r in records if r["kind"] == "memory"), {})
        innovations = []
        for r in [x for x in records if x["kind"] == "innovation"][-limit:]:
            decisions = [d for d in records if d["kind"] == "decision" and d.get("innovation_id") == r["id"]]
            outcomes = set(d["outcome"] for d in decisions)
            assessment = "Contested" if "Supported" in outcomes and "Refuted" in outcomes else (decisions[-1]["outcome"] if decisions else "Untested")
            innovations.append({"id": r["id"], "title": r["title"][:180], "status": r["status"], "assessment": assessment, "version": r["version"]})
        return {"goal": goal["title"][:600], "mode": goal["mode"], "primary_innovation": goal["primary_innovation"], "innovations": innovations,
                "counts": dict(Counter(r["status"] for r in experiments)),
                "recent_experiments": [{"id": r["id"], "title": r["title"][:180], "status": r["status"]} for r in experiments[-limit:]],
                "key_results": [{k: r.get(k) for k in ("id", "experiment_id", "status", "metric_improved", "acceptance_met", "drift")} for r in records if r["kind"] == "audit"][-limit:],
                "failed_routes": [{"id": r["id"], "title": r["title"][:180], "status": r["status"]} for r in experiments if r["status"] in ("Failed", "Deviated", "Unverified")][-limit:],
                "current_task": str(memory.get("current_task", "Review pending contracts"))[:600],
                "next_steps": [x[:300] for x in memory.get("next_steps", [])[:limit]],
                "unresolved": [x[:300] for x in memory.get("unresolved", [])[:limit]],
                "archive_records": len(records)}

    def resume(self):
        s = self.status()
        lines = ["# Research State", "", "Goal: " + s["goal"], "Mode: " + s["mode"], "Primary: " + str(s["primary_innovation"]), "", "Current task: " + s["current_task"], "", "## Innovations"]
        lines += ["- {id}: {title} ({status}; {assessment})".format(**r) for r in s["innovations"]]
        lines += ["", "## Recent experiments"] + ["- {id}: {title} — {status}".format(**r) for r in s["recent_experiments"]]
        lines += ["", "## Failed / uncertain routes"] + ["- {id}: {status}".format(**r) for r in s["failed_routes"]]
        lines += ["", "## Next steps"] + ["- " + x for x in s["next_steps"]]
        lines += ["", "## Unresolved"] + ["- " + x for x in s["unresolved"]]
        lines += ["", "Use history with an ID for full contracts, method cards, raw evidence and decisions. Resume is read-only; it never starts an experiment.", ""]
        return "\n".join(lines)

    def history(self, query="", kind=None, limit=20):
        found = []
        for event in self.store.events():
            for r in event["records"]:
                if (not kind or r["kind"] == kind) and query.casefold() in canonical(r).casefold():
                    found.append(r)
        return found[-limit:]
