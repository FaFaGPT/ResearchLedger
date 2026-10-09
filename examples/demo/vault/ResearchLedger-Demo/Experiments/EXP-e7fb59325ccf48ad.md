---
id: "EXP-e7fb59325ccf48ad"
type: "experiment"
title: "Median vs mean under fixed contamination"
status: "Completed"
version: 4
created: "2026-10-09T02:21:16.722480+00:00"
updated: "2026-10-09T02:21:17.011026+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Audits/AUD-cbe6ebb7805a4df0]]", "[[ResearchLedger-Demo/Evidence/EVI-986d05356b784e5f]]", "[[ResearchLedger-Demo/Evidence/EVI-af46436803b34c35]]", "[[ResearchLedger-Demo/Hypotheses/HYP-49c9d0a16ae24f19]]", "[[ResearchLedger-Demo/Innovations/INN-277686a18aba4327]]", "[[ResearchLedger-Demo/Methods/MET-8c5a1e5fc1654aef]]", "[[ResearchLedger-Demo/Runs/RUN-7c62c40f281448bc]]"]
---

# Median vs mean under fixed contamination

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Audits/AUD-cbe6ebb7805a4df0]]
- [[ResearchLedger-Demo/Evidence/EVI-986d05356b784e5f]]
- [[ResearchLedger-Demo/Evidence/EVI-af46436803b34c35]]
- [[ResearchLedger-Demo/Hypotheses/HYP-49c9d0a16ae24f19]]
- [[ResearchLedger-Demo/Innovations/INN-277686a18aba4327]]
- [[ResearchLedger-Demo/Methods/MET-8c5a1e5fc1654aef]]
- [[ResearchLedger-Demo/Runs/RUN-7c62c40f281448bc]]

## Record

````json
{
  "approval": {
    "fingerprint": "a24721a17d64a150eaa624d3b086500a74063ac57658aac2d0e83636099eb872",
    "reason": "Demo approval: fixed code/config, paired seeds, 10 seconds, 64 KiB output",
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
      "experiment.py"
    ],
    "command": [
      "{python}",
      "experiment.py"
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
    "title": "Median vs mean under fixed contamination",
    "training": "No learned parameters; deterministic estimator"
  },
  "created_at": "2026-10-09T02:21:16.722480+00:00",
  "evidence": [
    "AUD-cbe6ebb7805a4df0",
    "MET-8c5a1e5fc1654aef"
  ],
  "fingerprint": "a24721a17d64a150eaa624d3b086500a74063ac57658aac2d0e83636099eb872",
  "hypothesis_id": "HYP-49c9d0a16ae24f19",
  "hypothesis_version": 1,
  "id": "EXP-e7fb59325ccf48ad",
  "innovation_id": "INN-277686a18aba4327",
  "innovation_version": 2,
  "inputs": {
    "config.json": {
      "bytes": 174,
      "sha256": "caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba"
    },
    "experiment.py": {
      "bytes": 1467,
      "sha256": "189343e9ecb87ee112b3a97cc1bc28298480fd3f52de487bf463bfcb1e0706d6"
    }
  },
  "invariants": {
    "robust": true
  },
  "kind": "experiment",
  "source": "auditor",
  "status": "Completed",
  "title": "Median vs mean under fixed contamination",
  "updated_at": "2026-10-09T02:21:17.011026+00:00",
  "version": 4
}
````
