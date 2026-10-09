"""Create and execute a new, small CPU research project. Never overwrite a directory."""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "skills/researchledger/scripts"))
from researchledger.engine import Ledger
from researchledger.runner import execute
from researchledger import obsidian


def build(output):
    root = Path(output).absolute()
    if root.exists():
        raise ValueError("Demo destination must not exist: " + str(root))
    root.mkdir(parents=True)
    for name in ("experiment.py", "config.json", "innovation.json"):
        shutil.copyfile(str(REPO / "examples/robust-location" / name), str(root / name))
    ledger = Ledger(root)
    ledger.init("Test robust location estimation under fixed sparse contamination")
    inv = ledger.add_innovation(json.loads((root / "innovation.json").read_text()))
    inv = ledger.evolve(inv["id"], "approve", "Pre-authorized public CPU demonstration of research management")
    template = json.loads((REPO / "skills/researchledger/assets/contract.json").read_text())
    template["innovation_id"] = inv["id"]
    (root / "contract.json").write_text(json.dumps(template, indent=2) + "\n")
    results = []
    exp = ledger.plan(template)
    ledger.approve(exp["id"], "Demo approval: fixed code/config, paired seeds, 10 seconds, 64 KiB output")
    results.append(execute(ledger, exp["id"], True))
    # The demo intentionally does not fabricate a human scientific approval.
    failure_code = "raise RuntimeError('Intentional failure case for ResearchLedger demonstration')\n"
    (root / "failure.py").write_text(failure_code)
    failed = dict(template, title="Failure route: intentional exception", code=["failure.py"], command=["{python}", "failure.py"])
    e2 = ledger.plan(failed); ledger.approve(e2["id"], "Authorized failure demonstration")
    results.append(execute(ledger, e2["id"], True))
    # A contradictory mechanism report exercises real audit behavior using computed metrics.
    original = (root / "experiment.py").read_text()
    (root / "drift.py").write_text(original.replace('"observed": config', '"observed": dict(config, robust=False)'))
    drift = dict(template, title="Drift route: improved metric with contradictory mechanism", code=["drift.py"], command=["{python}", "drift.py"])
    e3 = ledger.plan(drift); ledger.approve(e3["id"], "Authorized drift-detection demonstration")
    results.append(execute(ledger, e3["id"], True))
    ledger.checkpoint("Review captured source and paired-seed evidence before making a scientific decision",
                      ["Review why the median improves this synthetic protocol", "Plan an explicit independent replication", "Test different contamination strengths after approval"],
                      ["No researcher scientific decision has been recorded", "External validity and novelty are not established", "A positive metric does not excuse contradictory mechanism evidence"])
    obsidian.init(ledger, "vault", "ResearchLedger-Demo")
    vault = root / "vault"; vault.mkdir()
    (vault / "Reading.md").write_text("# Robust location estimation\n\nPersonal literature note. Median robustness is established statistical knowledge; this toy experiment makes no novelty claim.\n", encoding="utf-8")
    ledger.literature("Robust estimation reading note", "note:Reading.md", [inv["id"]])
    obsidian.sync(ledger)
    assert obsidian.sync(ledger)["written"] == 0
    (root / "DEMO_RESULTS.json").write_text(json.dumps([{k: r[k] for k in ("experiment_id", "status", "execution_success", "metric_improved", "acceptance_met", "mean_delta", "drift")} for r in results], indent=2) + "\n")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        for result in build(args.output):
            print(result["experiment_id"], result["status"], "delta=", result["mean_delta"])
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + "\n")
