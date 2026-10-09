"""Read-only release checks for tracked artifacts, integrity and generated links."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/researchledger/scripts"))
from researchledger.engine import Ledger
from researchledger import obsidian
from researchledger.store import LedgerError


def check():
    errors, count = [], 0
    p = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), stdout=subprocess.PIPE, check=True)
    names = p.stdout.decode().split("\0")
    patterns = [r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----", r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}",
                r"sk-[A-Za-z0-9_-]{35,}", r"AKIA[A-Z0-9]{16}", r"[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/][^\s\"']+", r"/home/[a-zA-Z0-9_-]+/"]
    for name in names:
        if not name:
            continue
        path = ROOT / name
        if not path.is_file():
            errors.append("Missing tracked file: " + name); continue
        raw = path.read_bytes(); count += 1
        try:
            text = raw.decode("utf-8")
        except UnicodeError:
            continue
        for pattern in patterns:
            if re.search(pattern, text):
                errors.append("Sensitive-looking content in " + name + " (match intentionally not printed)")
                break
    skill = ROOT / "skills/researchledger"
    body = (skill / "SKILL.md").read_text(encoding="utf-8")
    if not body.startswith("---\nname: researchledger\ndescription: "):
        errors.append("Invalid skill frontmatter")
    for match in re.findall(r"\]\(([^)]+)\)", body):
        if not (skill / match).is_file():
            errors.append("Missing skill reference: " + match)
    demo = ROOT / "examples/demo"
    if not demo.exists():
        errors.append("Generated demo is missing")
    else:
        try:
            ledger = Ledger(demo)
            ledger.store.events()
            for blob in (ledger.store.home / "blobs").iterdir():
                ledger.store.read_blob({"sha256": blob.name})
            if not obsidian.inspect(ledger)["up_to_date"]:
                errors.append("Demo vault is stale or conflicted")
            vault = demo / "vault"
            for path in vault.rglob("*.md"):
                for target in re.findall(r"\[\[([^\]]+)\]\]", path.read_text(encoding="utf-8")):
                    resolved = vault / target
                    if not resolved.is_file() and not resolved.with_suffix(".md").is_file():
                        errors.append("Broken vault link: " + target)
        except (LedgerError, ValueError, OSError) as exc:
            errors.append("Demo verification: " + str(exc))
    return {"tracked_files_scanned": count, "errors": errors, "passed": not errors}


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
