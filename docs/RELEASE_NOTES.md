# ResearchLedger 0.1.0

First public release of **ResearchLedger — Innovation-Driven Research Management for Coding Agents**.

## Included

- A self-contained Codex Skill and zero-runtime-dependency Python CLI.
- Innovation registry, executable experiment contracts, captured method provenance, evidence/deviation audits and persistent research memory.
- Strict, Bounded and budgeted Explore policies with explicit scientific-review gates.
- Optional one-way Obsidian synchronization, Dashboard, native Bases views, literature links and protected personal notes.
- A real CPU experiment, failure/drift examples, complete evidence archive and example vault.
- MIT license, English documentation, automated tests and Windows/Linux CI.

## Release assets

- `researchledger-skill.zip`: extract the `researchledger` directory into a Codex skill discovery directory.
- `ResearchLedger-source.zip`: full tracked source, examples, evidence and documentation.
- `researchledger-0.1.0-py3-none-any.whl`: install with `python -m pip install PATH_TO_WHEEL`.
- `SHA256SUMS.json`: integrity checksums for the three distributable assets.

The source also includes `tools/install_skill.py --destination YOUR_SKILL_DIRECTORY`, which refuses to overwrite an existing installation. See README.md for discovery locations and usage.

## Scope

This is a cooperative local research controller, not a hostile-code sandbox or an automatic judge of scientific validity. Captured evidence and structural verification remain distinct from researcher-reviewed conclusions. Obsidian is optional. Cloud-specific MLflow/W&B/DVC adapters are future work; the offline adapter boundary is available now. Read SECURITY.md and docs/TEST_REPORT.md for tested guarantees and limitations.
