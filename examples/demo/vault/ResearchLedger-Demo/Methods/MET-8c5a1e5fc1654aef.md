---
id: "MET-8c5a1e5fc1654aef"
type: "method"
title: "MET-8c5a1e5fc1654aef"
status: "Recorded"
version: 1
created: "2026-10-09T02:21:17.011026+00:00"
updated: "2026-10-09T02:21:17.011026+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Evidence/EVI-986d05356b784e5f]]", "[[ResearchLedger-Demo/Evidence/EVI-af46436803b34c35]]", "[[ResearchLedger-Demo/Experiments/EXP-e7fb59325ccf48ad]]", "[[ResearchLedger-Demo/Runs/RUN-7c62c40f281448bc]]"]
---

# MET-8c5a1e5fc1654aef

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Evidence/EVI-986d05356b784e5f]]
- [[ResearchLedger-Demo/Evidence/EVI-af46436803b34c35]]
- [[ResearchLedger-Demo/Experiments/EXP-e7fb59325ccf48ad]]
- [[ResearchLedger-Demo/Runs/RUN-7c62c40f281448bc]]

Captured input `config.json`: [[ResearchLedger-Demo/Raw/caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba.txt]]

Captured input `experiment.py`: [[ResearchLedger-Demo/Raw/189343e9ecb87ee112b3a97cc1bc28298480fd3f52de487bf463bfcb1e0706d6.txt]]

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
    "experiment.py": {
      "bytes": 1467,
      "sha256": "189343e9ecb87ee112b3a97cc1bc28298480fd3f52de487bf463bfcb1e0706d6"
    }
  },
  "code_changes": [],
  "command": [
    "{python}",
    "experiment.py"
  ],
  "core_functions": {
    "experiment.py": [
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
  "created_at": "2026-10-09T02:21:17.011026+00:00",
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
    "EVI-af46436803b34c35",
    "EVI-986d05356b784e5f"
  ],
  "execution_flow": "Runner receipt -> captured source/config -> process -> raw log/result -> paired comparison",
  "experiment_id": "EXP-e7fb59325ccf48ad",
  "git_commit": "28a1b2e25093c4618d17c858ed85e28be9f94aa3",
  "git_status": "M skills/researchledger/scripts/researchledger/adapters.py\n M skills/researchledger/scripts/researchledger/audit.py\n M skills/researchledger/scripts/researchledger/cli.py\n M skills/researchledger/scripts/researchledger/runner.py\n M skills/researchledger/scripts/researchledger/schema.py\n M skills/researchledger/scripts/researchledger/store.py\n?? .github/\n?? LICENSE\n?? README.md\n?? SECURITY.md\n?? docs/ADAPTERS.md\n?? docs/USE_CASES.md\n?? examples/demo/\n?? tests/test_boundaries.py\n?? tools/",
  "id": "MET-8c5a1e5fc1654aef",
  "kind": "method",
  "motivation": "A small number of outliers can dominate mean estimation error.",
  "principle": "Use the sample median to limit the influence of large outliers.",
  "results": {
    "acceptance_met": true,
    "drift": [],
    "execution_success": true,
    "mean_delta": -2.9660657447821346,
    "metric_improved": true,
    "status": "Completed",
    "unknown": []
  },
  "run_id": "RUN-7c62c40f281448bc",
  "runtime_call_trace": "Unknown",
  "scientific_validity": "Unknown until researcher review; declarations are not execution proof",
  "source": "auditor",
  "training_declared": "No learned parameters; deterministic estimator",
  "updated_at": "2026-10-09T02:21:17.011026+00:00",
  "version": 1
}
````
