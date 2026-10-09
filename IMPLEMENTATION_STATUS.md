# Implementation status

Resume here, then run `python -m unittest discover -s tests -v`.

## Milestones

- M0: Official-source research and architecture complete.
- M1: Append-only storage, schemas, innovation registry — complete.
- M2: Contracts, controlled runner, provenance and audit — complete; 18 tests pass.
- M3: Research memory, CLI and Codex skill — complete.
- M4: Protected Obsidian projections — implemented; 28 cumulative tests pass. Example vault pending.
- M5: Functional/security review, documentation and packaging — pending.
- M6: GitHub publication — pending; portable GitHub CLI downloaded and official checksum verified.

## Decisions

- `.research/events.jsonl` is the authoritative record; state is a disposable projection.
- One event contains one atomic multi-record transaction with a hash-chain link.
- Evidence is captured as SHA-256 addressed blobs; integrity is not scientific validity.
- Commands are read-only unless explicitly requesting a mutation. `run` is a preflight by default.
- Human approvals are recorded attestations, not an authentication/security boundary.
- Execution is cooperative local process control, not a hostile-code sandbox.
- Native Markdown, Properties and Bases only; no Obsidian dependency or third-party plugins.

## Open issues

- Complete implementation and tests before any public push.
- GitHub authentication must be performed by the user if unavailable.
