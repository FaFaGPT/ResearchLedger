# CLI workflow and schemas

All commands can use `python <skill-dir>/scripts/ledger.py`; an installed package also provides `researchledger`. Global flags precede the command: `--project ROOT`, `--actor agent|researcher`, `--details`. JSON input file paths are relative to the shell's current directory; contract input paths are relative to the project. Record IDs are returned by each creation command. No commands silently execute training.

```text
init "Scientific goal"
--actor researcher innovation add innovation.json
--actor researcher innovation approve INN-ID --reason "Researcher's authorization"
plan contract.json
--actor researcher approve EXP-ID --reason "Authorized scope, command and budget"
run EXP-ID
run EXP-ID --execute
audit EXP-ID
audit EXP-ID --save
--details history EXP-ID
--actor researcher decision EXP-ID Supported --reason "Scoped conclusion" --review review.md
checkpoint memory.json
resume
```

`innovation add` requires title, motivation, mechanism, contribution, origin, and `invariants` mapping top-level config keys to expected JSON values. Optional literature is a list of registered literature IDs. Sources: Researcher-Defined, Researcher-Proposed, AI-Proposed. Candidate → Active (`approve`), Paused, Rejected, Superseded (`replace`), Split; `revise --data FILE` adds a revision and returns to Candidate. `split` and `replace` require `--targets ID ...`. These transitions require a reason and researcher attribution. `innovation primary ID --reason TEXT` changes the goal's primary only to an Active innovation. Direction changes invalidate version-pinned experiments.

Copy [../assets/contract.json](../assets/contract.json) and replace the innovation ID and project-specific fields. Required contract fields are enforced by `scripts/researchledger/schema.py` (unknown fields are rejected). Contracts pin the innovation version, input bytes and execution identity. Code/config input files must exist when planning. Use `replication_of` and `replication_reason` to intentionally repeat an existing fingerprint. Substantive changes require a new contract and approval.

The project configuration is a JSON object containing `model`, `dataset`, `algorithm`, `metric`, `seeds`, and the innovation invariant keys. It may include additional hyperparameters. Include dependency locks and dataset manifests in `code` so their bytes enter the evidence store. Keep actual large datasets outside the small execution worktree; use versioned manifests and explicitly review their real contents.

The runner passes `RESEARCHLEDGER_CONFIG` (absolute config file) and `RESEARCHLEDGER_RESULT` (unique result destination). Commands are argv lists with no shell interpretation. `{python}` resolves to the current interpreter. The experimental script writes the result JSON described in [audit.md](audit.md). Every attempt gets a distinct directory; repeating requires a new contract.

V1 requires exactly `wall-time budget` and `output budget` in `stop_conditions`. Unsupported declared rules are rejected rather than silently ignored. Encode domain-specific stops in the approved program. Preflight rejects missing/mismatched config and innovation invariants before starting the process.

`checkpoint FILE` requires `current_task` (text), `next_steps` and `unresolved` (text lists). History searches all revisions and returns a compact last-20 list by default; `--kind` and `--limit` refine it.

## Exploration

```text
--actor researcher policy Explore --scope exploration.json
```

Scope requires `innovations: [IDs]`, `allowed_changes: [glob patterns]`, `max_runs`, `max_total_seconds`, `branch_prefix: "explore/my-study/"`. The contract must set `exploratory: true`, run on a matching Git branch, and use change patterns explicitly present in the policy. All exploratory attempts, including failed and interrupted attempts, reserve their full wall-time budget cumulatively. Policy changes do not erase past consumption. Prepare the branch using the existing Git workflow; ResearchLedger never checks out a branch automatically. Strict/Bounded policies ignore autonomous exploration and require exact approval.

## Ledger schema

`events.jsonl`: `schema=1, seq, id, time, source, action, previous, records, hash`. Each record includes `id, kind, version, created_at, updated_at, source, evidence`; kind-specific fields are validated at the mutation boundary. Event hashes use SHA-256 over canonical sorted compact UTF-8 JSON excluding the hash field. `previous` is the prior event hash. Full revisions are appended; there are no in-place record edits or delete APIs. IDs are opaque UUID-derived identifiers, never filesystem input from a title.

Record kinds: goal, innovation, hypothesis, experiment, run, evidence, method, audit, decision, memory, literature, candidate, obsidian. State snapshots are disposable; replay is authoritative. Blobs live under `blobs/<sha256>`. A writer lock protects transactions; reads may fail closed during an incomplete append and can be retried. Back up the entire `.research/` directory together.
