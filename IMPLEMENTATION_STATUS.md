# Implementation status

Resume here, then run `python -m unittest discover -s tests -v`.

## Milestones

- M0: Official-source research and architecture complete.
- M1: Append-only storage, schemas, innovation registry — complete.
- M2: Contracts, controlled runner, provenance and audit — complete; 18 tests pass.
- M3: Research memory, CLI and Codex skill — complete.
- M4: Protected Obsidian projections and real example vault — complete.
- M5: Functional/security review, documentation and packaging — complete; 39 tests pass on Windows Python 3.8, 3.10 and 3.12. Wheel build/install and standalone skill validation pass.
- M6: Public repository created at https://github.com/FaFaGPT/ResearchLedger. Source push awaits GitHub OAuth workflow scope for the included CI configuration.

## Decisions

- `.research/events.jsonl` is the authoritative record; state is a disposable projection.
- One event contains one atomic multi-record transaction with a hash-chain link.
- Evidence is captured as SHA-256 addressed blobs; integrity is not scientific validity.
- Commands are read-only unless explicitly requesting a mutation. `run` is a preflight by default.
- Human approvals are recorded attestations, not an authentication/security boundary.
- Execution is cooperative local process control, not a hostile-code sandbox.
- Native Markdown, Properties and Bases only; no Obsidian dependency or third-party plugins.

## Open issues

- Independent installed wheel and fresh Git clone validation passed, including all 39 tests and byte-exact demo evidence.
- Linux execution will be verified in GitHub CI; native Obsidian UI rendering has not been exercised locally.

## Validation fixes

- Closed subprocess output pipes after the initial test exposed a resource warning.
- Reject duplicate JSON fields, NaN and infinities while preserving malformed raw evidence as Unverified.
- Reject unsupported declarative stop rules; domain-specific rules belong in approved code.
- Check config and innovation boundaries before execution, not only in the post-run audit.
- Preserve exact evidence and generated-vault bytes in Git to prevent newline conversion breaking hashes.
