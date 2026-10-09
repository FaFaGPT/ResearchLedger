# Validation report

Date: 2026-10-09. This report records executed checks, not intended capabilities.

## Automated tests

`python -m unittest discover -s tests -v`: **39 passed**, no skipped tests, on Windows with Python **3.8.6**, **3.10.8**, and **3.12.14**. Tests execute actual small subprocesses; they do not substitute canned runner receipts. The standalone installer test copies the skill to a temporary directory and invokes its own entrypoint.

| Area | Evidence |
| --- | --- |
| Storage | Replay, full revision history, stale version refusal, hash corruption, truncated writes, blob tampering, writer lock |
| Scientific workflow | Real paired-metric success, explicit scientific review gate, failure, missing evidence, innovation drift despite gain, unfair compute comparison |
| Execution boundaries | Exact approval/input pins, changed innovation invalidation, preflight config mismatch, wall-time/output stops, unsupported stop rejection |
| Explore policy | Independent Git branch, authorized innovation scope, cumulative reservation budget, no formal promotion of exploration |
| Method provenance | Python function extraction, captured source/config, raw logs/results, reconstructable changed-input diffs |
| Memory/CLI | New Ledger instance restores state, read-only status/resume/audit, duplicate detection and explicit replication |
| Obsidian | Repeated sync writes zero files and preserves timestamps, incremental updates, interrupted-write retry, unmanaged collision and human-note protection |
| Paths/links | Traversal rejection, Windows directory-junction rejection, generated wikilink resolution, existing literature note preservation |
| Invalid evidence | NaN and duplicate JSON fields retained as raw evidence but classified Unverified |
| Packaging | Independent installed-skill entrypoint, no-overwrite installer |

## Real example results

The committed demo ran a fixed synthetic robustness comparison over seeds 11, 22 and 33, with 100 paired trials per seed:

- Success: Completed; mean treatment-minus-baseline MSE **-2.9660657447821346**; acceptance met.
- Intentional exception: Failed; no scientific inference.
- Contradictory mechanism report: Deviated with innovation drift; the same numerical improvement does not validate the method.

No human scientific decision was fabricated for the demo; it remains ready for review. Original source/config/log/result artifacts and the ledger are included under `examples/demo/.research/`.

## Skill and release checks

- Bundled `skill-creator/scripts/quick_validate.py`: **Skill is valid** (Python UTF-8 mode is needed for the validator on legacy Windows locales).
- `tools/release_check.py`: tracked-file secret/personal-path pattern scan, example journal/blob integrity, generated-view freshness and all vault wikilinks passed.
- Byte-preserving Git attributes prevent newline normalization of evidence and manifest-controlled outputs.
- Python wheel built successfully using the installed build backend and installed into an isolated target directory; its CLI read the example ledger successfully. The host's configured package proxy blocked isolated dependency downloading, so the build used `--no-build-isolation` with existing setuptools/wheel.
- A Windows/Linux GitHub Actions matrix is included; live CI results are recorded after publication.

## Scope and remaining limitations

Obsidian files were checked against official syntax and all links were resolved programmatically. Native Obsidian UI rendering was not exercised in this environment; no screenshot is claimed. Statistical validity, model semantics, authentication, hard GPU/RAM/spending quotas and malicious subprocess isolation are outside the automated guarantees. See SECURITY.md and the audit reference. The configured Python 3.13 launcher on the development host was stale and could not start; no Python 3.13 result is claimed.
