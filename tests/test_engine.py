import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/researchledger/scripts"))
from researchledger.engine import Ledger
from researchledger.runner import execute
from researchledger.audit import audit
from researchledger.store import LedgerError
from helpers import setup_project, contract


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger, self.inv = setup_project(self.root)

    def run_exp(self, code=None, config=None, changes=None):
        if code is not None:
            (self.root / "experiment.py").write_text(code, encoding="utf-8")
        if config:
            data = json.loads((self.root / "config.json").read_text())
            data.update(config)
            (self.root / "config.json").write_text(json.dumps(data))
        c = contract(self.inv)
        if changes:
            c.update(changes)
        e = self.ledger.plan(c)
        self.ledger.approve(e["id"], "Approved controlled test")
        return e, execute(self.ledger, e["id"], True)

    def test_real_success_and_review_gate(self):
        e, result = self.run_exp()
        self.assertEqual(result["status"], "Completed")
        self.assertTrue(result["metric_improved"])
        self.assertTrue(result["acceptance_met"])
        self.assertEqual(self.ledger.get(e["hypothesis_id"])["status"], "Untested")
        (self.root / "review.md").write_text("Reviewed code, paired data, estimator mechanism and metric. Scope is the synthetic protocol only.")
        self.ledger.decision(e["id"], "Supported", "Meets specified toy hypothesis", "review.md")
        self.assertEqual(self.ledger.get(e["hypothesis_id"])["status"], "Supported")
        cards = self.ledger.history(e["id"], "method")
        self.assertTrue(cards[0]["core_functions"]["experiment.py"])
        self.assertEqual(cards[0]["runtime_call_trace"], "Unknown")

    def test_failure(self):
        _, result = self.run_exp("raise RuntimeError('intentional test failure')\n")
        self.assertEqual(result["status"], "Failed")
        self.assertFalse(result["execution_success"])

    def test_missing_evidence(self):
        _, result = self.run_exp("print('No metrics produced')\n")
        self.assertEqual(result["status"], "Unverified")

    def test_deviation(self):
        code = (self.root / "experiment.py").read_text() + "\nPath('forbidden.txt').write_text('changed')\n"
        _, result = self.run_exp(code)
        self.assertEqual(result["status"], "Deviated")
        self.assertTrue(result["metric_improved"])

    def test_innovation_drift_despite_metric_gain(self):
        # Keep computed treatment values but explicitly report a contradictory mechanism.
        code = (self.root / "experiment.py").read_text().replace('"observed": config', '"observed": dict(config, robust=False)')
        _, result = self.run_exp(code)
        self.assertTrue(result["metric_improved"])
        self.assertEqual(result["status"], "Deviated")
        self.assertTrue(result["drift"])

    def test_unfair_comparison(self):
        code = (self.root / "experiment.py").read_text().replace('"compute_budget": 100', '"compute_budget": 100 if variant == "baseline" else 200')
        _, result = self.run_exp(code)
        self.assertEqual(result["status"], "Deviated")

    def test_budget_stop(self):
        _, result = self.run_exp("import time\ntime.sleep(5)\n", changes={"budget": {"max_seconds": 0.1, "max_output_bytes": 2048}})
        self.assertEqual(result["status"], "Failed")

    def test_output_stop(self):
        _, result = self.run_exp("print('x' * 100000)\n", changes={"budget": {"max_seconds": 3, "max_output_bytes": 2048}})
        self.assertEqual(result["status"], "Failed")

    def test_duplicate_and_replication(self):
        c = contract(self.inv)
        e = self.ledger.plan(c)
        with self.assertRaises(LedgerError):
            self.ledger.plan(c)
        c.update(replication_of=e["id"], replication_reason="Independent rerun")
        self.assertNotEqual(self.ledger.plan(c)["id"], e["id"])

    def test_read_only_resume_and_audit(self):
        e, _ = self.run_exp()
        self.ledger.checkpoint("Inspect robustness", ["Test another contamination level"], ["External validity unknown"])
        before = self.ledger.store.journal.read_bytes()
        fresh = Ledger(self.root)
        self.assertIn("Inspect robustness", fresh.resume())
        self.assertIn("External validity", fresh.resume())
        audit(fresh, e["id"])
        self.assertEqual(before, fresh.store.journal.read_bytes())

    def test_approval_and_input_pin(self):
        e = self.ledger.plan(contract(self.inv))
        self.assertFalse(execute(self.ledger, e["id"])["ready"])
        self.ledger.approve(e["id"], "Approve")
        self.assertTrue(execute(self.ledger, e["id"])["ready"])
        (self.root / "config.json").write_text("{}")
        with self.assertRaises(LedgerError):
            execute(self.ledger, e["id"], True)

    def test_revision_revokes_approval(self):
        e = self.ledger.plan(contract(self.inv))
        self.ledger.approve(e["id"], "Approve")
        self.ledger.evolve(self.inv["id"], "pause", "Reconsider mechanism")
        self.assertFalse(execute(self.ledger, e["id"])["ready"])

    def test_tampered_evidence_blocks_conclusion(self):
        e, _ = self.run_exp()
        blob = self.ledger.history(e["id"], "evidence")[0]["artifact"]["sha256"]
        (self.ledger.store.home / "blobs" / blob).write_bytes(b"tampered")
        self.assertEqual(audit(self.ledger, e["id"])["status"], "Unverified")
        (self.root / "review.md").write_text("Review")
        with self.assertRaises(LedgerError):
            self.ledger.decision(e["id"], "Supported", "Claim", "review.md")

    def test_agent_cannot_change_direction(self):
        with self.assertRaises(LedgerError):
            self.ledger.evolve(self.inv["id"], "pause", "Agent guess", source="agent")
        with self.assertRaises(LedgerError):
            self.ledger.set_primary(self.inv["id"], "Agent guess", source="agent")


if __name__ == "__main__":
    unittest.main()
