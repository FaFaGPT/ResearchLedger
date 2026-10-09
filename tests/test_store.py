import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/researchledger/scripts"))
from researchledger.store import Store, LedgerError, confined, record


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)

    def test_replay_and_versions(self):
        r = record("innovation", {"title": "A"}, "test")
        with self.store.lock(create=True):
            self.store.append([r], "create", "test")
            newer = record("innovation", {"title": "B"}, "test", r)
            self.store.append([newer], "revise", "test")
            with self.assertRaises(LedgerError):
                self.store.append([r], "stale", "test")
        self.assertEqual(self.store.records()[r["id"]]["title"], "B")
        self.assertEqual(len(self.store.events()), 2)

    def test_corruption_and_truncation_fail_closed(self):
        with self.store.lock(create=True):
            self.store.append([record("goal", {"title": "A"}, "test")], "init", "test")
        raw = self.store.journal.read_bytes()
        self.store.journal.write_bytes(raw.replace(b'"A"', b'"B"'))
        with self.assertRaises(LedgerError):
            self.store.records()
        self.store.journal.write_bytes(raw[:-1])
        with self.assertRaises(LedgerError):
            self.store.records()

    def test_path_and_lock_protection(self):
        for path in ("../x", "a/../b", "C:/x", "/x", "a\\b", "CON", "x."):
            with self.assertRaises(LedgerError):
                confined(self.tmp.name, path)
        with self.store.lock(create=True):
            with self.assertRaises(LedgerError):
                with self.store.lock():
                    pass

    def test_blob_integrity(self):
        self.store.home.mkdir()
        ref = self.store.blob(b"raw evidence")
        self.assertEqual(self.store.read_blob(ref), b"raw evidence")
        (self.store.home / "blobs" / ref["sha256"]).write_bytes(b"changed")
        with self.assertRaises(LedgerError):
            self.store.read_blob(ref)


if __name__ == "__main__":
    unittest.main()
