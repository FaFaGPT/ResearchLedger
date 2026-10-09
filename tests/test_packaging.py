import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from install_skill import install


class PackagingTests(unittest.TestCase):
    def test_standalone_install_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            target = install(Path(root) / "skills")
            self.assertTrue((target / "SKILL.md").is_file())
            project = Path(root) / "project"; project.mkdir()
            entry = target / "scripts/ledger.py"
            p = subprocess.run([sys.executable, str(entry), "--project", str(project), "init", "Installed skill smoke test"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(p.returncode, 0, p.stderr)
            p = subprocess.run([sys.executable, str(entry), "--project", str(project), "resume"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn(b"Installed skill smoke test", p.stdout)
            with self.assertRaises(ValueError):
                install(Path(root) / "skills")
