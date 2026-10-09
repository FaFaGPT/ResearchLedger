"""Opt-in cooperative local execution; not a security sandbox."""
import ast
import difflib
import fnmatch
import json
import os
import platform
import signal
import subprocess
import sys
import threading
import time

from . import schema
from .store import LedgerError, canonical, confined, digest, parse_json, record, uid


EXCLUDED = {".git", ".research", "__pycache__", ".venv", "node_modules"}


def git(root, *args):
    try:
        p = subprocess.run(["git"] + list(args), cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10)
        return p.stdout.decode("utf-8", "replace").strip() if p.returncode == 0 else "Unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "Unknown"


def snapshot(root):
    result, total = {}, 0
    for base, dirs, files in os.walk(str(root), followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for d in dirs:
            confined(root, (os.path.relpath(os.path.join(base, d), str(root))).replace(os.sep, "/"))
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(base, name), str(root)).replace(os.sep, "/")
            path = confined(root, rel)
            size = path.stat().st_size
            total += size
            schema.require(total <= 256 * 1024 * 1024 and len(result) < 20000, "V1 workspace snapshot limit exceeded (256 MiB / 20000 files); use a small dedicated worktree with data manifests")
            result[rel] = digest(path.read_bytes())
    return result


def preflight(ledger, experiment_id):
    exp = ledger.get(experiment_id, "experiment")
    goal = ledger.goal()
    inv = ledger.get(exp["innovation_id"], "innovation")
    errors = []
    if exp["status"] != "Planned":
        errors.append("Experiment already attempted; create an explicit replication contract")
    if inv["version"] != exp["innovation_version"]:
        errors.append("Innovation revision changed; replan")
    if inv["status"] in ("Paused", "Rejected", "Split", "Superseded"):
        errors.append("Innovation is inactive")
    for name, ref in exp["inputs"].items():
        try:
            if digest(confined(ledger.store.root, name).read_bytes()) != ref["sha256"]:
                errors.append("Planned input changed: " + name)
        except (OSError, LedgerError):
            errors.append("Missing/unsafe planned input: " + name)
    try:
        observed = parse_json(confined(ledger.store.root, exp["contract"]["config"]).read_bytes())
        schema.require(isinstance(observed, dict), "Config must be an object")
        for key in ("model", "dataset", "algorithm", "metric", "seeds"):
            if observed.get(key) != exp["contract"][key]:
                errors.append("Preflight configuration mismatch: " + key)
        for key, expected in exp["invariants"].items():
            if key not in observed or observed[key] != expected:
                errors.append("Preflight innovation boundary mismatch: " + key)
    except (OSError, ValueError):
        errors.append("Unreadable or invalid experiment configuration")
    sandbox = goal["mode"] == "Explore" and exp["contract"].get("exploratory", False)
    if sandbox:
        policy = goal["exploration"]
        if inv["id"] not in policy["innovations"]:
            errors.append("Innovation outside exploration scope")
        if not git(ledger.store.root, "branch", "--show-current").startswith(policy["branch_prefix"]):
            errors.append("Exploration requires its authorized independent Git branch")
        # Exact pattern membership is deliberately conservative; no unsafe glob-subset inference.
        if not set(exp["contract"]["allowed_changes"]).issubset(set(policy["allowed_changes"])):
            errors.append("Changes outside exploration policy")
        runs = [r for r in ledger.store.records().values() if r["kind"] == "run" and r.get("exploratory")]
        reserved = sum(r["reserved_seconds"] for r in runs)
        if len(runs) >= policy["max_runs"] or reserved + exp["contract"]["budget"]["max_seconds"] > policy["max_total_seconds"]:
            errors.append("Cumulative exploration budget exhausted")
    elif not exp["approval"] or exp["approval"]["fingerprint"] != exp["fingerprint"] or inv["status"] != "Active":
        errors.append("Exact contract requires researcher approval")
    return {"experiment_id": experiment_id, "ready": not errors, "errors": errors, "command": exp["contract"]["command"], "budget": exp["contract"]["budget"], "executes": False}


def stop_tree(process):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait()


def execute(ledger, experiment_id, execute=False, source="agent"):
    if not execute:
        return preflight(ledger, experiment_id)
    from .audit import persist_audit
    with ledger.store.lock():
        check = preflight(ledger, experiment_id)
        schema.require(check["ready"], "; ".join(check["errors"]))
        exp = ledger.get(experiment_id, "experiment")
        c = exp["contract"]
        before = snapshot(ledger.store.root)
        run_id = uid("RUN")
        output = confined(ledger.store.home, "runs/" + run_id + "/result.json")
        output.parent.mkdir(parents=True, exist_ok=False)
        config_raw = confined(ledger.store.root, c["config"]).read_bytes()
        try:
            config = parse_json(config_raw)
            schema.require(isinstance(config, dict), "Configuration must be a JSON object")
        except ValueError:
            raise LedgerError("Configuration must be valid JSON")
        functions = {}
        for name in c["code"]:
            if name.endswith(".py"):
                try:
                    tree = ast.parse(ledger.store.read_blob(exp["inputs"][name]).decode("utf-8-sig"))
                    functions[name] = [{"name": n.name, "line": n.lineno} for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                except (SyntaxError, UnicodeError):
                    functions[name] = "Unknown"
        command = [sys.executable if x == "{python}" else x for x in c["command"]]
        run = record("run", {"experiment_id": experiment_id, "status": "Running", "command": c["command"], "config": config,
                             "config_artifact": ledger.store.blob(config_raw), "inputs": exp["inputs"], "functions": functions,
                             "git_commit": git(ledger.store.root, "rev-parse", "HEAD"), "git_branch": git(ledger.store.root, "branch", "--show-current"),
                             "git_status": git(ledger.store.root, "status", "--porcelain"), "before": before,
                             "environment": {"python": platform.python_version(), "system": platform.system(), "machine": platform.machine()},
                             "reserved_seconds": c["budget"]["max_seconds"], "exploratory": c.get("exploratory", False)}, source)
        run["id"] = run_id
        ledger.save([run, record("experiment", dict(exp, status="Running"), source, exp)], "run.start", source)
        env = dict(os.environ)
        env.update({"RESEARCHLEDGER_RESULT": str(output), "RESEARCHLEDGER_CONFIG": str(confined(ledger.store.root, c["config"])), "PYTHONDONTWRITEBYTECODE": "1"})
        log = bytearray()
        exceeded = threading.Event()
        limit = c["budget"]["max_output_bytes"]
        start = time.monotonic()
        process, stopped, error = None, None, None
        try:
            kwargs = {"start_new_session": True} if os.name != "nt" else {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
            process = subprocess.Popen(command, cwd=str(ledger.store.root), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, **kwargs)

            def drain():
                while True:
                    chunk = process.stdout.read(4096)
                    if not chunk:
                        return
                    remaining = max(0, limit - len(log))
                    log.extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        exceeded.set()

            reader = threading.Thread(target=drain, daemon=True)
            reader.start()
            while process.poll() is None:
                if time.monotonic() - start >= c["budget"]["max_seconds"]:
                    stopped = "wall-time budget"
                if exceeded.is_set() or (output.exists() and output.stat().st_size > limit):
                    stopped = "output budget"
                if stopped:
                    stop_tree(process)
                    break
                time.sleep(0.02)
            reader.join(timeout=2)
            if reader.is_alive():
                stopped = "child process retained output pipe"
                stop_tree(process)
                reader.join(timeout=2)
            if exceeded.is_set():
                stopped = "output budget"
            exit_code = process.returncode
            if not reader.is_alive():
                process.stdout.close()
        except (OSError, KeyboardInterrupt) as exc:
            if process is not None:
                stop_tree(process)
                process.stdout.close()
            error = type(exc).__name__
            exit_code = -1
        elapsed = time.monotonic() - start
        evidence = [record("evidence", {"experiment_id": experiment_id, "run_id": run_id, "type": "execution-log", "artifact": ledger.store.blob(bytes(log))}, "runner")]
        report = None
        # Revalidate child-controlled output path before reading it.
        try:
            output = confined(ledger.store.home, "runs/" + run_id + "/result.json")
            if output.is_file() and output.stat().st_size <= limit:
                raw = output.read_bytes()
                evidence.append(record("evidence", {"experiment_id": experiment_id, "run_id": run_id, "type": "result-json", "artifact": ledger.store.blob(raw)}, "runner"))
                report = parse_json(raw)
            elif output.exists():
                stopped = "output budget"
        except (ValueError, OSError) as exc:
            error = "Invalid/missing report: " + type(exc).__name__
        try:
            after = snapshot(ledger.store.root)
            changes = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        except (LedgerError, OSError):
            after, changes = {}, ["Unknown"]
            error = "Workspace snapshot failed"
        code_changes = []
        for name in changes:
            if name not in exp["inputs"]:
                continue
            old_ref = exp["inputs"][name]
            try:
                path = confined(ledger.store.root, name)
                schema.require(not path.exists() or path.stat().st_size <= 16 * 1024 * 1024, "Changed source too large")
                raw = path.read_bytes() if path.exists() else b""
                new_ref = ledger.store.blob(raw)
                old_text = ledger.store.read_blob(old_ref).decode("utf-8", "replace").splitlines(True)
                new_text = raw.decode("utf-8", "replace").splitlines(True)
                diff = "".join(difflib.unified_diff(old_text, new_text, fromfile="before/" + name, tofile="after/" + name))
                code_changes.append({"path": name, "before": old_ref, "after": new_ref, "diff": ledger.store.blob(diff.encode()), "deleted": not path.exists()})
            except (LedgerError, OSError):
                code_changes.append({"path": name, "before": old_ref, "after": "Unknown"})
        final = record("run", dict(run, status="Finished", exit_code=exit_code, stopped=stopped, error=error, elapsed_seconds=round(elapsed, 6),
                                    after=after, changes=changes, code_changes=code_changes, report=report, evidence=[r["id"] for r in evidence]), "runner", run)
        ledger.save(evidence + [final], "run.finish", "runner")
        return persist_audit(ledger, final, locked=True)
