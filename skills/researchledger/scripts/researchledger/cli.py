"""Compact default output; explicit writes and opt-in execution."""
import argparse
import json
import sys
from pathlib import Path

from .engine import Ledger
from .store import LedgerError, parse_json


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8-sig"))


def parser():
    p = argparse.ArgumentParser(description="ResearchLedger — innovation-driven research management")
    p.add_argument("--project", default=".", help="Existing research project root")
    p.add_argument("--actor", choices=("agent", "researcher"), default="agent", help="Record researcher only with actual authorization; this is an attestation, not authentication")
    p.add_argument("--details", action="store_true", help="Expand full records/evidence metadata")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("init"); q.add_argument("goal")
    for name in ("status", "resume"):
        sub.add_parser(name)
    q = sub.add_parser("plan"); q.add_argument("contract", help="JSON contract file")
    q = sub.add_parser("audit"); q.add_argument("id"); q.add_argument("--save", action="store_true")
    q = sub.add_parser("history"); q.add_argument("query", nargs="?", default=""); q.add_argument("--kind"); q.add_argument("--limit", type=int, default=20)
    q = sub.add_parser("innovation"); q.add_argument("action", choices=("add", "approve", "revise", "split", "pause", "reject", "replace", "primary")); q.add_argument("value"); q.add_argument("--reason"); q.add_argument("--data"); q.add_argument("--targets", nargs="*")
    q = sub.add_parser("approve"); q.add_argument("id"); q.add_argument("--reason", required=True)
    q = sub.add_parser("run"); q.add_argument("id"); q.add_argument("--execute", action="store_true")
    q = sub.add_parser("policy"); q.add_argument("mode", choices=("Strict", "Bounded", "Explore")); q.add_argument("--scope")
    q = sub.add_parser("checkpoint"); q.add_argument("file", help="JSON current_task, next_steps, unresolved")
    q = sub.add_parser("decision"); q.add_argument("id"); q.add_argument("outcome", choices=("Supported", "Refuted", "Inconclusive")); q.add_argument("--reason", required=True); q.add_argument("--review", required=True)
    q = sub.add_parser("literature"); q.add_argument("title"); q.add_argument("locator"); q.add_argument("--innovations", nargs="*", default=[])
    q = sub.add_parser("evidence"); q.add_argument("id"); q.add_argument("--raw", action="store_true")
    q = sub.add_parser("obsidian"); o = q.add_subparsers(dest="obsidian_cmd", required=True)
    a = o.add_parser("init"); a.add_argument("vault"); a.add_argument("--namespace")
    o.add_parser("sync"); o.add_parser("status")
    a = o.add_parser("candidate"); a.add_argument("note")
    return p


def dispatch(a):
    ledger = Ledger(a.project)
    if a.cmd == "init": return ledger.init(a.goal, a.actor)
    if a.cmd == "status": return ledger.status()
    if a.cmd == "resume": return ledger.resume()
    if a.cmd == "plan": return ledger.plan(read_json(a.contract), a.actor)
    if a.cmd == "history":
        if not 1 <= a.limit <= 1000: raise LedgerError("limit must be 1..1000")
        return ledger.history(a.query, a.kind, a.limit)
    if a.cmd == "innovation":
        if a.action == "add": return ledger.add_innovation(read_json(a.value), a.actor)
        if a.action == "primary": return ledger.set_primary(a.value, a.reason, a.actor)
        return ledger.evolve(a.value, a.action, a.reason, a.actor, read_json(a.data) if a.data else None, a.targets)
    if a.cmd == "approve": return ledger.approve(a.id, a.reason, a.actor)
    if a.cmd == "run":
        from .runner import execute
        return execute(ledger, a.id, a.execute, a.actor)
    if a.cmd == "audit":
        from .audit import audit
        return audit(ledger, a.id, a.save)
    if a.cmd == "policy": return ledger.policy(a.mode, read_json(a.scope) if a.scope else None, a.actor)
    if a.cmd == "checkpoint":
        from .schema import fields
        data = read_json(a.file)
        fields(data, ("current_task", "next_steps", "unresolved"))
        return ledger.checkpoint(source=a.actor, **data)
    if a.cmd == "decision": return ledger.decision(a.id, a.outcome, a.reason, a.review, a.actor)
    if a.cmd == "literature": return ledger.literature(a.title, a.locator, a.innovations, a.actor)
    if a.cmd == "evidence":
        r = ledger.get(a.id, "evidence")
        return ledger.store.read_blob(r["artifact"]).decode("utf-8", "replace") if a.raw else r
    if a.cmd == "obsidian":
        from . import obsidian
        if a.obsidian_cmd == "init": return obsidian.init(ledger, a.vault, a.namespace)
        if a.obsidian_cmd == "sync": return obsidian.sync(ledger)
        if a.obsidian_cmd == "status": return obsidian.inspect(ledger)
        if a.obsidian_cmd == "candidate": return obsidian.candidate(ledger, a.note)
    raise LedgerError("Unknown command")


def compact(value):
    if isinstance(value, list): return [compact(v) for v in value]
    if isinstance(value, dict) and "kind" in value:
        return {k: value[k] for k in ("id", "kind", "version", "title", "status", "outcome", "experiment_id", "execution_success", "metric_improved", "acceptance_met", "drift", "deviations", "unknown") if k in value}
    return value


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = dispatch(args)
        if not args.details:
            result = compact(result)
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (LedgerError, OSError, ValueError) as exc:
        print("ResearchLedger: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
