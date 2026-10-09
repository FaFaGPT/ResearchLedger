"""Build distributable archives from tracked source and a self-contained skill."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package(destination):
    destination = Path(destination).absolute()
    destination.mkdir(parents=True, exist_ok=True)
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=str(ROOT)).decode().split("\0")
    outputs = []
    for name, prefix, entries in (
        ("ResearchLedger-source.zip", "ResearchLedger/", [n for n in names if n]),
        ("researchledger-skill.zip", "", [n for n in names if n.startswith("skills/researchledger/")]),
    ):
        target = destination / name
        if target.exists():
            raise ValueError("Archive already exists: " + str(target))
        with zipfile.ZipFile(str(target), "x", zipfile.ZIP_DEFLATED) as archive:
            for entry in entries:
                archive_name = prefix + entry if prefix else entry[len("skills/"):]
                archive.write(str(ROOT / entry), archive_name)
        outputs.append({"file": name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "bytes": target.stat().st_size})
    checksum = destination / "SHA256SUMS.json"
    if checksum.exists():
        raise ValueError("Checksum file already exists")
    checksum.write_text(json.dumps(outputs, indent=2) + "\n", encoding="utf-8")
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    print(json.dumps(package(parser.parse_args().output), indent=2))
