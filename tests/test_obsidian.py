import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/researchledger/scripts"))
from researchledger import obsidian
from researchledger.runner import execute
from researchledger.store import LedgerError
from helpers import setup_project, contract


class ObsidianTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger, self.inv = setup_project(self.root)
        self.vault = self.root / "vault"
        obsidian.init(self.ledger, "vault", "ResearchLedger-Test")
        self.managed = self.vault / "ResearchLedger-Test"

    def test_idempotent_sync_and_links(self):
        exp = self.ledger.plan(contract(self.inv))
        self.ledger.approve(exp["id"], "Test")
        execute(self.ledger, exp["id"], True)
        first = obsidian.sync(self.ledger)
        self.assertGreater(first["written"], 0)
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.managed.rglob("*") if p.is_file()}
        journal = self.ledger.store.journal.read_bytes()
        self.assertEqual(obsidian.sync(self.ledger)["written"], 0)
        self.assertEqual(self.ledger.store.journal.read_bytes(), journal)
        self.assertEqual(before, {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.managed.rglob("*") if p.is_file()})
        for p in self.managed.rglob("*.md"):
            for target in re.findall(r"\[\[([^\]]+)\]\]", p.read_text(encoding="utf-8")):
                dest = self.vault / target
                self.assertTrue(dest.is_file() or dest.with_suffix(".md").is_file(), target)
        base = json.loads((self.managed / "Research.base").read_text())
        self.assertEqual(len(base["views"]), 4)

    def test_manual_note_protection(self):
        obsidian.sync(self.ledger)
        dashboard = self.managed / "Dashboard.md"
        dashboard.write_text("Personal writing", encoding="utf-8")
        self.assertTrue(obsidian.inspect(self.ledger)["conflicts"])
        journal = self.ledger.store.journal.read_bytes()
        with self.assertRaises(LedgerError):
            obsidian.sync(self.ledger)
        self.assertEqual(dashboard.read_text(), "Personal writing")
        self.assertEqual(journal, self.ledger.store.journal.read_bytes())

    def test_unmanaged_collision_and_existing_vault(self):
        self.managed.mkdir(parents=True)
        (self.managed / "Dashboard.md").write_text("Existing note")
        with self.assertRaises(LedgerError):
            obsidian.sync(self.ledger)
        self.assertFalse((self.managed / "Research.base").exists())

    def test_incremental_update_preserves_unrelated_notes(self):
        obsidian.sync(self.ledger)
        manual = self.vault / "My Thoughts.md"
        manual.write_text("Author-owned")
        inv = self.managed / "Innovations" / (self.inv["id"] + ".md")
        stamp = inv.stat().st_mtime_ns
        self.ledger.checkpoint("Next question", ["Vary outlier count"], [])
        result = obsidian.sync(self.ledger)
        self.assertGreater(result["written"], 0)
        self.assertEqual(inv.stat().st_mtime_ns, stamp)
        self.assertEqual(manual.read_text(), "Author-owned")

    def test_candidate_import_does_not_promote(self):
        self.vault.mkdir()
        (self.vault / "Idea.md").write_text("Try a trimmed mean")
        r = obsidian.candidate(self.ledger, "Idea.md")
        self.assertEqual(r["status"], "PendingReview")
        self.assertEqual(obsidian.candidate(self.ledger, "Idea.md")["id"], r["id"])
        self.assertEqual(len(self.ledger.status()["innovations"]), 1)

    def test_existing_literature_note_link(self):
        self.vault.mkdir()
        (self.vault / "Reading.md").write_text("Original reading note")
        self.ledger.literature("Robust statistics", "note:Reading.md", [self.inv["id"]])
        obsidian.sync(self.ledger)
        self.assertEqual((self.vault / "Reading.md").read_text(), "Original reading note")
        self.assertIn("[[Reading]]", next((self.managed / "Literature").glob("*.md")).read_text())

    def test_traversal_and_namespace(self):
        with self.assertRaises(LedgerError):
            obsidian.candidate(self.ledger, "../config.json")
        # init validates namespace before touching files, even for a fresh project.
        other = self.root / "other"
        other.mkdir()
        ledger, _ = setup_project(other)
        with self.assertRaises(LedgerError):
            obsidian.init(ledger, "vault", "../escape")

    def test_interrupted_sync_recovers(self):
        original = obsidian.atomic_write
        calls = []
        def interrupted(path, data):
            calls.append(path)
            if len(calls) == 2:
                raise OSError("Simulated disk interruption")
            original(path, data)
        with patch.object(obsidian, "atomic_write", side_effect=interrupted):
            with self.assertRaises(OSError):
                obsidian.sync(self.ledger)
        self.assertIsNotNone(obsidian.config(self.ledger)["pending"])
        obsidian.sync(self.ledger)
        self.assertTrue(obsidian.inspect(self.ledger)["up_to_date"])


if __name__ == "__main__":
    unittest.main()
