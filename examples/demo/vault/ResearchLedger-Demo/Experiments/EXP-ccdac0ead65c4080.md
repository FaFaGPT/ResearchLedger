---
id: "EXP-ccdac0ead65c4080"
type: "experiment"
title: "Failure route: intentional exception"
status: "Failed"
version: 4
created: "2026-10-09T02:21:17.035745+00:00"
updated: "2026-10-09T02:21:17.270088+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Audits/AUD-d991e41e3a384308]]", "[[ResearchLedger-Demo/Evidence/EVI-3929a82e66f84c70]]", "[[ResearchLedger-Demo/Hypotheses/HYP-479f6886d62b434f]]", "[[ResearchLedger-Demo/Innovations/INN-277686a18aba4327]]", "[[ResearchLedger-Demo/Methods/MET-4f421ccf86b14e3f]]", "[[ResearchLedger-Demo/Runs/RUN-c306c88f2f5842ef]]"]
---

# Failure route: intentional exception

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Audits/AUD-d991e41e3a384308]]
- [[ResearchLedger-Demo/Evidence/EVI-3929a82e66f84c70]]
- [[ResearchLedger-Demo/Hypotheses/HYP-479f6886d62b434f]]
- [[ResearchLedger-Demo/Innovations/INN-277686a18aba4327]]
- [[ResearchLedger-Demo/Methods/MET-4f421ccf86b14e3f]]
- [[ResearchLedger-Demo/Runs/RUN-c306c88f2f5842ef]]

## Record

````json
{
  "approval": {
    "fingerprint": "af9c3dc50644b8c713a6ca86653af4e4cb9ac05b3f2e4996647f11c92322b9ab",
    "reason": "Authorized failure demonstration",
    "source": "researcher"
  },
  "contract": {
    "acceptance": {
      "direction": "minimize",
      "min_delta": 0.5,
      "min_pairs": 3
    },
    "algorithm": "median-vs-mean",
    "allowed_changes": [],
    "budget": {
      "max_output_bytes": 65536,
      "max_seconds": 10
    },
    "code": [
      "failure.py"
    ],
    "command": [
      "{python}",
      "failure.py"
    ],
    "config": "config.json",
    "data_processing": "Seeded Gaussian samples plus two +20 outliers",
    "dataset": "synthetic-contamination-v1",
    "evaluation": "100 paired contaminated samples per seed",
    "forbidden_changes": [
      "config.json",
      "experiment.py"
    ],
    "hypothesis": "The median reduces MSE by at least 0.5 under fixed contamination.",
    "innovation_id": "INN-277686a18aba4327",
    "metric": "mse",
    "model": "location-estimator",
    "purpose": "Evaluate robustness under a controlled synthetic protocol",
    "seeds": [
      11,
      22,
      33
    ],
    "stop_conditions": [
      "wall-time budget",
      "output budget"
    ],
    "title": "Failure route: intentional exception",
    "training": "No learned parameters; deterministic estimator"
  },
  "created_at": "2026-10-09T02:21:17.035745+00:00",
  "evidence": [
    "AUD-d991e41e3a384308",
    "MET-4f421ccf86b14e3f"
  ],
  "fingerprint": "af9c3dc50644b8c713a6ca86653af4e4cb9ac05b3f2e4996647f11c92322b9ab",
  "hypothesis_id": "HYP-479f6886d62b434f",
  "hypothesis_version": 1,
  "id": "EXP-ccdac0ead65c4080",
  "innovation_id": "INN-277686a18aba4327",
  "innovation_version": 2,
  "inputs": {
    "config.json": {
      "bytes": 174,
      "sha256": "caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba"
    },
    "failure.py": {
      "bytes": 81,
      "sha256": "8a08df38389794c1c0682d7169d223bf9f3c884eb3773a0bbc6ab37c4638c19d"
    }
  },
  "invariants": {
    "robust": true
  },
  "kind": "experiment",
  "source": "auditor",
  "status": "Failed",
  "title": "Failure route: intentional exception",
  "updated_at": "2026-10-09T02:21:17.270088+00:00",
  "version": 4
}
````
