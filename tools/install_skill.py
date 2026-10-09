"""Explicit, no-overwrite standalone skill installation."""
import argparse
import shutil
from pathlib import Path


def install(destination):
    source = Path(__file__).resolve().parents[1] / "skills/researchledger"
    parent = Path(destination).expanduser().absolute()
    target = parent / "researchledger"
    if target.exists() or target.is_symlink():
        raise ValueError("Installation already exists; inspect it before upgrading: " + str(target))
    for ancestor in [parent] + list(parent.parents):
        if ancestor.is_symlink() or (ancestor.exists() and getattr(ancestor.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("Install destination cannot use linked/reparse paths")
    parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(source), str(target), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, help="Explicit skill parent directory; never overwritten")
    args = parser.parse_args()
    try:
        print("Installed: " + str(install(args.destination)))
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + "\n")
