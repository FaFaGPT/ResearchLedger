# Implementation status

Resume here, then run `python -m unittest discover -s tests -v`.

## Milestones

- M0: Official-source research and architecture complete.
- M1: Append-only storage, schemas, innovation registry — complete.
- M2: Contracts, controlled runner, provenance and audit — complete; 18 tests pass.
- M3: Research memory, CLI and Codex skill — complete.
- M4: Protected Obsidian projections and real example vault — complete.
- M5: Functional/security review, documentation and packaging — complete; 39 tests pass on Windows Python 3.8, 3.10 and 3.12. Wheel build/install and standalone skill validation pass.
- M6: Source published at https://github.com/FaFaGPT/ResearchLedger; all four Windows/Linux CI jobs passed. Version 0.1.0 release artifacts are prepared with SHA-256 checksums.

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
- No blocking implementation issues remain. Native Obsidian UI rendering has not been exercised locally; file syntax, links, integrity and synchronization are verified automatically.

## Published validation

- CI: https://github.com/FaFaGPT/ResearchLedger/actions/runs/37875189661
- Matrix: Ubuntu/Windows with Python 3.8/3.12; 39 tests and release checks passed in every job.
- Release location: https://github.com/FaFaGPT/ResearchLedger/releases/tag/v0.1.0

## Validation fixes

- Closed subprocess output pipes after the initial test exposed a resource warning.
- Reject duplicate JSON fields, NaN and infinities while preserving malformed raw evidence as Unverified.
- Reject unsupported declarative stop rules; domain-specific rules belong in approved code.
- Check config and innovation boundaries before execution, not only in the post-run audit.
- Preserve exact evidence and generated-vault bytes in Git to prevent newline conversion breaking hashes.
