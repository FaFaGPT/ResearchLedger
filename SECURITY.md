# Security and trust scope

ResearchLedger is intended for cooperative researchers and coding agents operating in an authorized local project. It is not an identity provider, execution isolation layer or cryptographically witnessed archive.

## Enforced checks

- Explicit execution flag, exact input pins, approval attribution, independent exploration branch and cumulative reservation checks.
- Shell-free argv execution, bounded wall time and captured log/result size; best-effort process-tree termination.
- Atomic single-event transactions, exclusive writer lock and fsync; corruption causes a hard failure.
- SHA-256 verification when reading captured evidence and before scientific promotion.
- Confined generated paths; rejection of traversal, symbolic links, Windows reparse points and unsafe path names.
- Manifest ownership and manual-edit conflict checks before vault writes; no delete/force-overwrite operation.
- Strict JSON, finite numbers, paired comparison consistency and Unknown for missing evidence.

## Limits

An approved subprocess inherits the current process environment and OS permissions. It can access external files, network and hardware, alter excluded files, or deliberately forge a report. The ledger and hash chain can also be rewritten by someone with filesystem access; hashes detect accidental corruption, not a malicious full-history rewrite. Use access controls, signed/remote backups and actual OS sandboxing where required. The `researcher` actor value is an attestation, not authenticated identity.

There is no hard RAM/GPU/cost/network quota. Wall-time polling can overshoot briefly, and process-tree termination cannot guarantee removal of deliberately detached descendants on every platform. Custom scientific stops belong in the approved experimental code; V1 rejects unimplemented declarative stop rules. External tool adapters do not execute remote code or auto-promote evidence.

Do not store credentials, private participant data or tokens in source/config/logs that will be captured. Obsidian synchronization intentionally copies evidence into the chosen vault. Release checks search tracked deliverables for common secret patterns and personal host paths; pattern scans are not a complete privacy audit.

Filesystem path checks and just-before-write hash checks address ordinary accidental conflicts, not an adversary racing filesystem calls. Use a trusted local filesystem and pause edits to generated notes while syncing.

If an execution is interrupted, its reservation remains spent. After verifying no process is using the ledger, a researcher can inspect and remove a stale `.research/write.lock`; the tool does not do so automatically. `audit EXP-ID --save` records an interrupted run as Unverified. For a corrupt journal, preserve the original and restore a verified backup; do not truncate history to make validation pass.

Report vulnerabilities privately to the repository maintainers through GitHub security reporting when enabled. Do not include private research artifacts in public issues.
