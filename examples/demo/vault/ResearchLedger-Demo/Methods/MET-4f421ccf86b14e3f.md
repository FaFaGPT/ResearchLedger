---
id: "MET-4f421ccf86b14e3f"
type: "method"
title: "MET-4f421ccf86b14e3f"
status: "Recorded"
version: 1
created: "2026-10-09T02:21:17.270088+00:00"
updated: "2026-10-09T02:21:17.270088+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Evidence/EVI-3929a82e66f84c70]]", "[[ResearchLedger-Demo/Experiments/EXP-ccdac0ead65c4080]]", "[[ResearchLedger-Demo/Runs/RUN-c306c88f2f5842ef]]"]
---

# MET-4f421ccf86b14e3f

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Evidence/EVI-3929a82e66f84c70]]
- [[ResearchLedger-Demo/Experiments/EXP-ccdac0ead65c4080]]
- [[ResearchLedger-Demo/Runs/RUN-c306c88f2f5842ef]]

Captured input `config.json`: [[ResearchLedger-Demo/Raw/caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba.txt]]

Captured input `failure.py`: [[ResearchLedger-Demo/Raw/8a08df38389794c1c0682d7169d223bf9f3c884eb3773a0bbc6ab37c4638c19d.txt]]

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
    "failure.py": {
      "bytes": 81,
      "sha256": "8a08df38389794c1c0682d7169d223bf9f3c884eb3773a0bbc6ab37c4638c19d"
    }
  },
  "code_changes": [],
  "command": [
    "{python}",
    "failure.py"
  ],
  "core_functions": {
    "failure.py": []
  },
  "created_at": "2026-10-09T02:21:17.270088+00:00",
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
    "EVI-3929a82e66f84c70"
  ],
  "execution_flow": "Runner receipt -> captured source/config -> process -> raw log/result -> paired comparison",
  "experiment_id": "EXP-ccdac0ead65c4080",
  "git_commit": "28a1b2e25093c4618d17c858ed85e28be9f94aa3",
  "git_status": "M skills/researchledger/scripts/researchledger/adapters.py\n M skills/researchledger/scripts/researchledger/audit.py\n M skills/researchledger/scripts/researchledger/cli.py\n M skills/researchledger/scripts/researchledger/runner.py\n M skills/researchledger/scripts/researchledger/schema.py\n M skills/researchledger/scripts/researchledger/store.py\n?? .github/\n?? LICENSE\n?? README.md\n?? SECURITY.md\n?? docs/ADAPTERS.md\n?? docs/USE_CASES.md\n?? examples/demo/\n?? tests/test_boundaries.py\n?? tools/",
  "id": "MET-4f421ccf86b14e3f",
  "kind": "method",
  "motivation": "A small number of outliers can dominate mean estimation error.",
  "principle": "Use the sample median to limit the influence of large outliers.",
  "results": {
    "acceptance_met": false,
    "drift": [],
    "execution_success": false,
    "mean_delta": null,
    "metric_improved": false,
    "status": "Failed",
    "unknown": [
      "Invalid report: Expected an object"
    ]
  },
  "run_id": "RUN-c306c88f2f5842ef",
  "runtime_call_trace": "Unknown",
  "scientific_validity": "Unknown until researcher review; declarations are not execution proof",
  "source": "auditor",
  "training_declared": "No learned parameters; deterministic estimator",
  "updated_at": "2026-10-09T02:21:17.270088+00:00",
  "version": 1
}
````
