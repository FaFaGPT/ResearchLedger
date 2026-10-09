# Tracker adapters

V1 includes a typed `EvidenceAdapter` protocol and a working `JsonEvidenceAdapter`, located in `skills/researchledger/scripts/researchledger/adapters.py`. The adapter reads an explicit local JSON export with `observed` and `trials`, validates its envelope and returns its SHA-256 source attribution. No network SDK is imported.

Future MLflow, W&B and DVC adapters should export code/config/dataset references plus the normalized evidence protocol. They must retain original run identifiers, immutable artifact hashes and source provenance, avoid putting credentials in records, and mark unavailable fields Unknown. Remote tracker status is not scientific verification. A normalization adapter must not create researcher approvals or formal conclusions.

Cloud-specific adapters are not implemented in V1. Existing integrations can normalize their output in the approved experiment script and write it to `RESEARCHLEDGER_RESULT`; the normal capture/audit path then applies. Large artifacts should be represented by verified manifests and reviewed external locators, not silently downloaded or assumed reproducible.
