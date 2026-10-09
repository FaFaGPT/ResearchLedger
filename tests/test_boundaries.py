import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/researchledger/scripts"))
from researchledger import obsidian
from researchledger.runner import execute
from researchledger.store import LedgerError, confined
from helpers import setup_project, contract


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger, self.inv = setup_project(self.root)

    def test_explore_branch_scope_and_cumulative_budget(self):
        subprocess.run(["git", "init", "-b", "main"], cwd=str(self.root), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        scope = {"innovations": [self.inv["id"]], "allowed_changes": [], "max_runs": 1, "max_total_seconds": 10, "branch_prefix": "explore/toy/"}
        self.ledger.policy("Explore", scope)
        c = contract(self.inv); c["exploratory"] = True
        e = self.ledger.plan(c)
        self.assertFalse(execute(self.ledger, e["id"])["ready"])
        subprocess.run(["git", "checkout", "-b", "explore/toy/median"], cwd=str(self.root), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertTrue(execute(self.ledger, e["id"])["ready"])
        self.assertEqual(execute(self.ledger, e["id"], True)["status"], "Completed")
        (self.root / "review.md").write_text("Exploration review")
        with self.assertRaises(LedgerError):
            self.ledger.decision(e["id"], "Supported", "Exploratory claim", "review.md")
        c.update(replication_of=e["id"], replication_reason="Budget test")
        second = self.ledger.plan(c)
        self.assertIn("budget", " ".join(execute(self.ledger, second["id"])["errors"]))

    def test_bounded_never_implicitly_executes(self):
        self.ledger.policy("Bounded")
        c = contract(self.inv); c["exploratory"] = True
        e = self.ledger.plan(c)
        with self.assertRaises(LedgerError):
            execute(self.ledger, e["id"], True)

    def test_evolution_history_split_replace_revise(self):
        data = {k: self.inv[k] for k in ("title", "motivation", "mechanism", "contribution", "origin", "invariants")}
        child1 = self.ledger.add_innovation(dict(data, title="Trimmed mean"))
        child2 = self.ledger.add_innovation(dict(data, title="Winsorization"))
        self.ledger.evolve(self.inv["id"], "split", "Separate mechanisms", targets=[child1["id"], child2["id"]])
        self.assertEqual(self.ledger.get(self.inv["id"])["status"], "Split")
        revised = self.ledger.evolve(child1["id"], "revise", "Clarify", data=dict(data, title="Revised"))
        self.assertEqual(revised["version"], 2)
        self.ledger.evolve(child1["id"], "replace", "Superseded", targets=[child2["id"]])
        self.assertEqual(len([r for r in self.ledger.history(child1["id"], "innovation") if r["id"] == child1["id"]]), 3)

    def test_code_change_has_reconstructable_diff(self):
        path = self.root / "experiment.py"
        path.write_text(path.read_text() + "\nPath('config.json').write_text('{}')\n")
        e = self.ledger.plan(contract(self.inv))
        self.ledger.approve(e["id"], "Test")
        result = execute(self.ledger, e["id"], True)
        self.assertEqual(result["status"], "Deviated")
        method = self.ledger.history(e["id"], "method")[0]
        change = method["code_changes"][0]
        self.assertEqual(self.ledger.store.read_blob(change["after"]), b"{}")
        self.assertIn(b"before/config.json", self.ledger.store.read_blob(change["diff"]))

    def test_nonfinite_metrics_never_verify(self):
        p = self.root / "experiment.py"
        p.write_text(p.read_text().replace('"value": evaluate(seed, variant == "treatment" and config["robust"])', '"value": float("nan")').replace('allow_nan=False', 'allow_nan=True'))
        e = self.ledger.plan(contract(self.inv)); self.ledger.approve(e["id"], "Test")
        self.assertEqual(execute(self.ledger, e["id"], True)["status"], "Unverified")

    def test_symlink_or_windows_junction_blocked(self):
        target = self.root / "outside"; target.mkdir()
        link = self.root / "linked"
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode:
                self.skipTest("Directory junction unavailable")
        else:
            link.symlink_to(target, target_is_directory=True)
        try:
            with self.assertRaises(LedgerError):
                confined(self.root, "linked/note.md")
            with self.assertRaises(LedgerError):
                obsidian.init(self.ledger, "linked")
        finally:
            if os.name == "nt":
                os.rmdir(str(link))
            else:
                link.unlink()

    def test_unsupported_stop_rule_rejected(self):
        c = contract(self.inv); c["stop_conditions"].append("stop at accuracy 0.99")
        with self.assertRaises(LedgerError):
            self.ledger.plan(c)

    def test_preflight_rejects_scientific_config_mismatch(self):
        p = self.root / "config.json"
        cfg = json.loads(p.read_text()); cfg["model"] = "unauthorized-model"
        p.write_text(json.dumps(cfg))
        e = self.ledger.plan(contract(self.inv)); self.ledger.approve(e["id"], "Approve declared scope")
        self.assertFalse(execute(self.ledger, e["id"])["ready"])
        with self.assertRaises(LedgerError):
            execute(self.ledger, e["id"], True)

    def test_duplicate_json_fields_never_verify(self):
        p = self.root / "experiment.py"
        p.write_text("import os\nfrom pathlib import Path\nPath(os.environ['RESEARCHLEDGER_RESULT']).write_text('{\"observed\": {}, \"observed\": {}, \"trials\": []}')\n")
        e = self.ledger.plan(contract(self.inv)); self.ledger.approve(e["id"], "Test")
        self.assertEqual(execute(self.ledger, e["id"], True)["status"], "Unverified")

    def test_finite_metrics_with_overflow_delta_never_verify(self):
        p = self.root / "experiment.py"
        p.write_text(p.read_text().replace('"value": evaluate(seed, variant == "treatment" and config["robust"])', '"value": 1e308 if variant == "baseline" else -1e308'))
        e = self.ledger.plan(contract(self.inv)); self.ledger.approve(e["id"], "Test")
        result = execute(self.ledger, e["id"], True)
        self.assertEqual(result["status"], "Unverified")
        self.assertFalse(result["acceptance_met"])
