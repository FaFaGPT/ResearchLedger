"""One-way projections with ownership manifests and conflict-first synchronization."""
import json
import os
import re
from pathlib import Path

from . import schema
from .store import LedgerError, atomic_write, canonical, confined, digest, record, relative

FOLDERS = {"goal": "Goals", "innovation": "Innovations", "hypothesis": "Hypotheses", "experiment": "Experiments", "run": "Runs",
           "method": "Methods", "audit": "Audits", "evidence": "Evidence", "decision": "Decisions", "literature": "Literature", "memory": "Memory", "candidate": "Candidates"}


def config(ledger):
    found = [r for r in ledger.store.records().values() if r["kind"] == "obsidian"]
    schema.require(found, "Use obsidian init first")
    return found[0]


def vault_path(ledger, cfg):
    path = Path(cfg["vault"])
    if not path.is_absolute():
        path = ledger.store.root / path
    path = Path(os.path.abspath(str(path)))
    # Do not resolve first; doing so could conceal a symlink/junction.
    confined(path.parent, path.name)
    return path


def init(ledger, vault, namespace=None):
    with ledger.store.lock():
        goal = ledger.goal()
        schema.require(not any(r["kind"] == "obsidian" for r in ledger.store.records().values()), "Vault already connected; use the existing connection")
        ns = namespace or "ResearchLedger-" + goal["id"]
        schema.require(bool(re.fullmatch(r"[A-Za-z0-9_-]{1,80}", ns)), "Namespace must be a safe single folder name")
        cfg = {"vault": str(vault), "namespace": ns, "files": {}, "pending": None}
        target = vault_path(ledger, cfg)
        schema.require(not target.exists() or target.is_dir(), "Vault path must be a directory")
        try:
            target.relative_to(ledger.store.home)
            raise LedgerError("Vault cannot be inside .research")
        except ValueError:
            pass
        managed = confined(target, ns)
        schema.require(not managed.exists(), "Namespace already exists; choose another to protect existing notes")
        # Keep portable relative paths where possible; no need to expose host paths in generated notes.
        try:
            cfg["vault"] = os.path.relpath(str(target), str(ledger.store.root)).replace(os.sep, "/")
        except ValueError:
            cfg["vault"] = str(target)
        r = record("obsidian", cfg, "researcher")
        ledger.save([r], "obsidian.init", "researcher")
    return {"namespace": ns, "configured": True, "sync_required": True}


def note_path(r):
    return FOLDERS[r["kind"]] + "/" + r["id"] + ".md"


def linked_ids(value, records):
    found = set()
    if isinstance(value, dict):
        for item in value.values():
            found.update(linked_ids(item, records))
    elif isinstance(value, list):
        for item in value:
            found.update(linked_ids(item, records))
    elif isinstance(value, str) and value in records:
        found.add(value)
    return found


def project(ledger, cfg):
    records = {k: v for k, v in ledger.store.records().items() if v["kind"] in FOLDERS}
    ns = cfg["namespace"]
    output = {}

    def link(rid):
        return "[[" + ns + "/" + note_path(records[rid])[:-3] + "]]"

    for rid, r in sorted(records.items()):
        related = linked_ids(r, records) - {rid}
        # Explicit reverse edges make dashboard -> innovation -> experiment -> evidence navigation useful.
        related.update(k for k, other in records.items() if k != rid and rid in linked_ids(other, records))
        front = {"id": rid, "type": r["kind"], "title": r.get("title", rid), "status": r.get("status", r.get("outcome", "Recorded")),
                 "version": r["version"], "created": r["created_at"], "updated": r["updated_at"], "source": r["source"], "managed_by": "ResearchLedger",
                 "links": [link(x) for x in sorted(related)]}
        body = ["---"] + [k + ": " + json.dumps(v, ensure_ascii=False) for k, v in front.items()] + ["---", "", "# " + str(r.get("title", rid)).replace("\n", " "), "", "> Generated view. Keep personal notes in separate files; manual edits here block synchronization.", "", "## Connections"]
        body += ["- " + link(x) for x in sorted(related)]
        if r["kind"] == "literature":
            locator = r["locator"]
            if locator.startswith("note:"):
                local = relative(locator[5:])
                schema.require(local.endswith(".md") and not any(x in local for x in "[]|#"), "Invalid literature note locator")
                schema.require(confined(vault_path(ledger, cfg), local).is_file(), "Existing literature note is missing: " + local)
                body += ["", "Existing note: [[" + local[:-3] + "]] (not managed by ResearchLedger)"]
        if r["kind"] == "evidence":
            raw = ledger.store.read_blob(r["artifact"])
            raw_name = "Raw/" + r["artifact"]["sha256"] + ".txt"
            output[raw_name] = raw
            body += ["", "Raw evidence: [[" + ns + "/" + raw_name + "]]", ""]
        if r["kind"] == "method":
            for name, ref in r["code_artifacts"].items():
                raw_name = "Raw/" + ref["sha256"] + ".txt"
                output[raw_name] = ledger.store.read_blob(ref)
                body += ["", "Captured input `" + name + "`: [[" + ns + "/" + raw_name + "]]"]
        body += ["", "## Record", "", "````json", json.dumps(r, ensure_ascii=False, indent=2, allow_nan=False), "````", ""]
        if r["kind"] == "innovation":
            body += ["## Revision history", ""]
            for old in ledger.history(rid, "innovation", 1000000):
                if old["id"] == rid:
                    body += ["- v%d — %s — %s" % (old["version"], old["updated_at"], old["status"])]
        output[note_path(r)] = "\n".join(body).encode()
    s = ledger.status()
    lines = ["---", "type: research-dashboard", "managed_by: ResearchLedger", "---", "", "# Research Dashboard", "", s["goal"], "",
             "**Mode:** " + s["mode"], "", "[[" + ns + "/Research State]] · [[" + ns + "/Research.base]]", "", "## Innovations", "", "| Innovation | Status | Assessment |", "| --- | --- | --- |"]
    for r in records.values():
        if r["kind"] == "innovation":
            decisions = [d["outcome"] for d in records.values() if d["kind"] == "decision" and d.get("innovation_id") == r["id"]]
            assessment = "Contested" if "Supported" in decisions and "Refuted" in decisions else (decisions[-1] if decisions else "Untested")
            lines.append("| %s | %s | %s |" % (link(r["id"]), r["status"], assessment))
    lines += ["", "## Experiments", "", "| Experiment | Status | Core result |", "| --- | --- | --- |"]
    for r in records.values():
        if r["kind"] == "experiment":
            audits = [a for a in records.values() if a["kind"] == "audit" and a["experiment_id"] == r["id"]]
            result = "Pending" if not audits else "delta=%s; drift=%s" % (audits[-1]["mean_delta"], bool(audits[-1]["drift"]))
            lines.append("| %s | %s | %s |" % (link(r["id"]), r["status"], result))
    lines += ["", "## Next experiment", "", "Use `plan` in Codex with an innovation ID and a testable hypothesis. Execution remains subject to the contract and approval.", ""]
    lines += ["- " + x for x in s["next_steps"]]
    lines += ["", "## Open questions", ""] + ["- " + x for x in s["unresolved"]]
    lines += ["", "## Recent decisions", ""] + ["- " + link(r["id"]) for r in list(records.values()) if r["kind"] == "decision"][-8:]
    output["Dashboard.md"] = "\n".join(lines).encode()
    output["Research State.md"] = ledger.resume().encode()
    base = {"filters": {"and": ['file.inFolder("' + ns + '")', 'managed_by == "ResearchLedger"']},
            "properties": {"note.title": {"displayName": "Title"}, "note.status": {"displayName": "Status"}},
            "views": [{"type": "table", "name": title, "filters": 'type == "' + kind + '"', "order": ["file.name", "note.title", "note.status", "note.version", "note.updated", "note.links"]}
                      for title, kind in (("Innovations", "innovation"), ("Experiments", "experiment"), ("Decisions", "decision"), ("Evidence", "evidence"))]}
    # JSON is a YAML subset and accepted by the native Bases parser.
    output["Research.base"] = (json.dumps(base, indent=2) + "\n").encode()
    return output


def inspect(ledger):
    cfg = config(ledger)
    root = confined(vault_path(ledger, cfg), cfg["namespace"])
    desired = project(ledger, cfg)
    changes, conflicts = [], []
    pending = cfg.get("pending") or {}
    for rel, data in desired.items():
        target = confined(root, rel)
        wanted = digest(data)
        old = cfg["files"].get(rel)
        recovering = pending.get(rel)
        if target.exists():
            if not target.is_file():
                conflicts.append(rel + ": path is not a file")
                continue
            actual = digest(target.read_bytes())
            if old is None and recovering is None:
                conflicts.append(rel + ": unmanaged existing file")
            elif actual not in {old, recovering}:
                conflicts.append(rel + ": manually changed")
            elif actual != wanted:
                changes.append(rel)
        else:
            changes.append(rel)
    return {"namespace": cfg["namespace"], "changes": changes, "conflicts": conflicts, "up_to_date": not changes and not conflicts, "files": len(desired)}


def sync(ledger):
    with ledger.store.lock():
        cfg = config(ledger)
        state = inspect(ledger)
        schema.require(not state["conflicts"], "Sync conflicts; preserve/move your notes before retrying: " + "; ".join(state["conflicts"]))
        if state["up_to_date"] and not cfg.get("pending"):
            return dict(state, written=0)
        desired = project(ledger, cfg)
        root = confined(vault_path(ledger, cfg), cfg["namespace"])
        hashes = {rel: digest(data) for rel, data in desired.items()}
        pending = record("obsidian", dict(cfg, pending=hashes), "exporter", cfg)
        ledger.save([pending], "obsidian.prepare", "exporter")
        for rel in state["changes"]:
            target = confined(root, rel)
            # Recheck just before replacement to catch ordinary concurrent edits.
            if target.exists():
                current = digest(target.read_bytes())
                schema.require(current in {cfg["files"].get(rel), (cfg.get("pending") or {}).get(rel)}, "Concurrent note edit: " + rel)
            atomic_write(target, desired[rel])
        complete = record("obsidian", dict(pending, files=hashes, pending=None), "exporter", pending)
        ledger.save([complete], "obsidian.sync", "exporter")
        return dict(state, written=len(state["changes"]), up_to_date=True)


def candidate(ledger, note):
    with ledger.store.lock():
        cfg = config(ledger)
        path = confined(vault_path(ledger, cfg), note)
        schema.require(path.is_file() and path.suffix == ".md" and path.stat().st_size <= 1024 * 1024, "Candidate must be a Markdown note up to 1 MiB")
        raw = path.read_bytes()
        sha = digest(raw)
        prior = [r for r in ledger.store.records().values() if r["kind"] == "candidate" and r["artifact"]["sha256"] == sha]
        if prior:
            return prior[0]
        r = record("candidate", {"title": path.stem, "note": note, "status": "PendingReview", "artifact": ledger.store.blob(raw)}, "obsidian-note")
        ledger.save([r], "candidate.import", "obsidian-note")
        return r
