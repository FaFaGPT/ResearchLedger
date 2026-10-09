"""Append-only transactions, confined paths and content-addressed evidence."""
import contextlib
import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


class LedgerError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def uid(prefix):
    return prefix + "-" + uuid.uuid4().hex[:16]


def relative(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or any(ord(c) < 32 for c in value):
        raise LedgerError("Expected a portable relative path")
    parts = value.split("/")
    if any(p in ("", ".", "..") or p.endswith((" ", ".")) for p in parts):
        raise LedgerError("Unsafe path: " + value)
    if any(re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", p, re.I) for p in parts):
        raise LedgerError("Reserved path: " + value)
    if PurePosixPath(value).is_absolute():
        raise LedgerError("Absolute paths are not allowed")
    return value


def confined(root, value):
    relative(value)
    root = Path(root).absolute()
    target = root.joinpath(*value.split("/"))
    # Check ancestors as well as descendants: junctions/reparse points count as links.
    for p in [target] + list(target.parents):
        if p.is_symlink() or (p.exists() and getattr(p.lstat(), "st_file_attributes", 0) & 0x400):
            raise LedgerError("Linked/reparse paths are not allowed: " + str(p))
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        raise LedgerError("Path escapes its root")
    return target


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp), str(path))
    finally:
        if tmp.exists():
            tmp.unlink()


class Store:
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.home = confined(self.root, ".research")
        self.journal = confined(self.root, ".research/events.jsonl")

    @contextlib.contextmanager
    def lock(self, create=False):
        if create:
            self.home.mkdir(parents=True, exist_ok=True)
        if not self.home.is_dir():
            raise LedgerError("No ledger; use init first")
        lock = confined(self.home, "write.lock")
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise LedgerError("Ledger is locked; inspect the recorded PID before manually recovering a stale lock")
        try:
            os.write(fd, canonical({"pid": os.getpid(), "time": now()}).encode())
            os.close(fd)
            yield
        finally:
            lock.unlink()

    def events(self):
        if not self.journal.exists():
            return []
        result, previous, versions = [], "0" * 64, {}
        with self.journal.open("rb") as f:
            for n, line in enumerate(f, 1):
                try:
                    if not line.endswith(b"\n"):
                        raise ValueError("incomplete transaction")
                    event = json.loads(line)
                    claimed = event.pop("hash")
                    if event["schema"] != 1 or event["seq"] != n or event["previous"] != previous or digest(canonical(event).encode()) != claimed:
                        raise ValueError("chain mismatch")
                    for record in event["records"]:
                        if record["version"] != versions.get(record["id"], 0) + 1:
                            raise ValueError("version mismatch")
                        versions[record["id"]] = record["version"]
                    event["hash"] = claimed
                    result.append(event)
                    previous = claimed
                except (KeyError, ValueError, TypeError) as exc:
                    raise LedgerError("Corrupt journal at line %d: %s" % (n, exc))
        return result

    def records(self):
        result = {}
        for event in self.events():
            result.update({r["id"]: r for r in event["records"]})
        return result

    def append(self, records, action, source):
        events = self.events()
        current = self.records()
        if len({r["id"] for r in records}) != len(records):
            raise LedgerError("Duplicate record in transaction")
        for record in records:
            old = current.get(record["id"])
            expected = old["version"] + 1 if old else 1
            if record["version"] != expected:
                raise LedgerError("Stale revision")
        event = {"schema": 1, "seq": len(events) + 1, "id": uid("EVT"), "time": now(),
                 "source": source, "action": action, "previous": events[-1]["hash"] if events else "0" * 64, "records": records}
        event["hash"] = digest(canonical(event).encode())
        with self.journal.open("ab") as f:
            f.write((canonical(event) + "\n").encode())
            f.flush()
            os.fsync(f.fileno())
        return event

    def blob(self, data):
        sha = digest(data)
        path = confined(self.home, "blobs/" + sha)
        if path.exists():
            if digest(path.read_bytes()) != sha:
                raise LedgerError("Corrupt existing evidence blob")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        return {"sha256": sha, "bytes": len(data)}

    def read_blob(self, ref):
        sha = ref["sha256"]
        if not re.fullmatch("[a-f0-9]{64}", sha):
            raise LedgerError("Invalid blob ID")
        try:
            data = confined(self.home, "blobs/" + sha).read_bytes()
        except OSError:
            raise LedgerError("Missing evidence blob: " + sha)
        if digest(data) != sha:
            raise LedgerError("Evidence integrity mismatch: " + sha)
        return data


def record(kind, data, source, old=None):
    stamp = now()
    result = dict(data)
    result.update({"id": old["id"] if old else uid(kind[:3].upper()), "kind": kind,
                   "version": old["version"] + 1 if old else 1,
                   "created_at": old["created_at"] if old else stamp, "updated_at": stamp,
                   "source": source, "evidence": data.get("evidence", [])})
    return result
