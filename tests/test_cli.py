import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/researchledger/scripts"))
from researchledger.cli import main
from helpers import setup_project, contract


class CliTests(unittest.TestCase):
    def test_core_commands(self):
        with tempfile.TemporaryDirectory() as root:
            ledger, inv = setup_project(root)
            path = Path(root) / "contract.json"
            path.write_text(json.dumps(contract(inv)))
            for args in (["status"], ["resume"], ["plan", str(path)], ["history", inv["id"]]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(["--project", root] + args), 0)
                    self.assertTrue(output.getvalue())
            exp = ledger.history(kind="experiment")[0]
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(["--project", root, "run", exp["id"]]), 0)
                self.assertFalse(json.loads(output.getvalue())["executes"])
            self.assertEqual(ledger.get(exp["id"])["status"], "Planned")

    def test_invalid_input_returns_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as root:
            with contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(main(["--project", root, "status"]), 2)
                self.assertNotIn("Traceback", error.getvalue())
