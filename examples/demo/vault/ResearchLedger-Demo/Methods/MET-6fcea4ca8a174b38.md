---
id: "MET-6fcea4ca8a174b38"
type: "method"
title: "MET-6fcea4ca8a174b38"
status: "Recorded"
version: 1
created: "2026-10-09T02:21:17.597605+00:00"
updated: "2026-10-09T02:21:17.597605+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Evidence/EVI-b6ca9b5ad37c429d]]", "[[ResearchLedger-Demo/Evidence/EVI-bce5a304f456486c]]", "[[ResearchLedger-Demo/Experiments/EXP-eee59c78bb664d6a]]", "[[ResearchLedger-Demo/Runs/RUN-5941db10b4164cdc]]"]
---

# MET-6fcea4ca8a174b38

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Evidence/EVI-b6ca9b5ad37c429d]]
- [[ResearchLedger-Demo/Evidence/EVI-bce5a304f456486c]]
- [[ResearchLedger-Demo/Experiments/EXP-eee59c78bb664d6a]]
- [[ResearchLedger-Demo/Runs/RUN-5941db10b4164cdc]]

Captured input `config.json`: [[ResearchLedger-Demo/Raw/caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba.txt]]

Captured input `drift.py`: [[ResearchLedger-Demo/Raw/55d2ead535ed2a02ffe4e9b7489309c8375be8c424f973fdc1cd017e366bc03d.txt]]

## Record

````json
{
  "captured_config": {
    "algorithm": "median-vs-mean",
    "dataset": "synthetic-contamination-v1",
    "metric": "mse",
    "model": "location-estimator",
    "robust": true,
    "seeds": [
      11,
      22,
      33
    ]
  },
  "changes": [],
  "code_artifacts": {
    "config.json": {
      "bytes": 174,
      "sha256": "caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba"
    },
    "drift.py": {
      "bytes": 1525,
      "sha256": "55d2ead535ed2a02ffe4e9b7489309c8375be8c424f973fdc1cd017e366bc03d"
    }
  },
  "code_changes": [],
  "command": [
    "{python}",
    "drift.py"
  ],
  "core_functions": {
    "drift.py": [
      {
        "line": 9,
        "name": "estimate_location"
      },
      {
        "line": 13,
        "name": "evaluate"
      },
      {
        "line": 24,
        "name": "main"
      }
    ]
  },
  "created_at": "2026-10-09T02:21:17.597605+00:00",
  "data_processing_declared": "Seeded Gaussian samples plus two +20 outliers",
  "declared_algorithm": "median-vs-mean",
  "dependency_lock": "Captured only when explicitly listed in contract.code; otherwise Unknown",
  "environment": {
    "machine": "AMD64",
    "python": "3.8.6",
    "system": "Windows"
  },
  "evaluation_declared": "100 paired contaminated samples per seed",
  "evidence": [
    "EVI-bce5a304f456486c",
    "EVI-b6ca9b5ad37c429d"
  ],
  "execution_flow": "Runner receipt -> captured source/config -> process -> raw log/result -> paired comparison",
  "experiment_id": "EXP-eee59c78bb664d6a",
  "git_commit": "28a1b2e25093c4618d17c858ed85e28be9f94aa3",
  "git_status": "M skills/researchledger/scripts/researchledger/adapters.py\n M skills/researchledger/scripts/researchledger/audit.py\n M skills/researchledger/scripts/researchledger/cli.py\n M skills/researchledger/scripts/researchledger/runner.py\n M skills/researchledger/scripts/researchledger/schema.py\n M skills/researchledger/scripts/researchledger/store.py\n?? .github/\n?? LICENSE\n?? README.md\n?? SECURITY.md\n?? docs/ADAPTERS.md\n?? docs/USE_CASES.md\n?? examples/demo/\n?? tests/test_boundaries.py\n?? tools/",
  "id": "MET-6fcea4ca8a174b38",
  "kind": "method",
  "motivation": "A small number of outliers can dominate mean estimation error.",
  "principle": "Use the sample median to limit the influence of large outliers.",
  "results": {
    "acceptance_met": true,
    "drift": [
      "Reported innovation drift: robust"
    ],
    "execution_success": true,
    "mean_delta": -2.9660657447821346,
    "metric_improved": true,
    "status": "Deviated",
    "unknown": []
  },
  "run_id": "RUN-5941db10b4164cdc",
  "runtime_call_trace": "Unknown",
  "scientific_validity": "Unknown until researcher review; declarations are not execution proof",
  "source": "auditor",
  "training_declared": "No learned parameters; deterministic estimator",
  "updated_at": "2026-10-09T02:21:17.597605+00:00",
  "version": 1
}
````
