---
id: "EXP-eee59c78bb664d6a"
type: "experiment"
title: "Drift route: improved metric with contradictory mechanism"
status: "Deviated"
version: 4
created: "2026-10-09T02:21:17.292662+00:00"
updated: "2026-10-09T02:21:17.597605+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Audits/AUD-4ee4e28655f849a5]]", "[[ResearchLedger-Demo/Evidence/EVI-b6ca9b5ad37c429d]]", "[[ResearchLedger-Demo/Evidence/EVI-bce5a304f456486c]]", "[[ResearchLedger-Demo/Hypotheses/HYP-24d283de28d64a4a]]", "[[ResearchLedger-Demo/Innovations/INN-277686a18aba4327]]", "[[ResearchLedger-Demo/Methods/MET-6fcea4ca8a174b38]]", "[[ResearchLedger-Demo/Runs/RUN-5941db10b4164cdc]]"]
---

# Drift route: improved metric with contradictory mechanism

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Audits/AUD-4ee4e28655f849a5]]
- [[ResearchLedger-Demo/Evidence/EVI-b6ca9b5ad37c429d]]
- [[ResearchLedger-Demo/Evidence/EVI-bce5a304f456486c]]
- [[ResearchLedger-Demo/Hypotheses/HYP-24d283de28d64a4a]]
- [[ResearchLedger-Demo/Innovations/INN-277686a18aba4327]]
- [[ResearchLedger-Demo/Methods/MET-6fcea4ca8a174b38]]
- [[ResearchLedger-Demo/Runs/RUN-5941db10b4164cdc]]

## Record

````json
{
  "approval": {
    "fingerprint": "f0986cdf7cb48c726a0339293c7c812ed8a5f1f38792b5922610cd5ae25ddca4",
    "reason": "Authorized drift-detection demonstration",
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
      "drift.py"
    ],
    "command": [
      "{python}",
      "drift.py"
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
    "title": "Drift route: improved metric with contradictory mechanism",
    "training": "No learned parameters; deterministic estimator"
  },
  "created_at": "2026-10-09T02:21:17.292662+00:00",
  "evidence": [
    "AUD-4ee4e28655f849a5",
    "MET-6fcea4ca8a174b38"
  ],
  "fingerprint": "f0986cdf7cb48c726a0339293c7c812ed8a5f1f38792b5922610cd5ae25ddca4",
  "hypothesis_id": "HYP-24d283de28d64a4a",
  "hypothesis_version": 1,
  "id": "EXP-eee59c78bb664d6a",
  "innovation_id": "INN-277686a18aba4327",
  "innovation_version": 2,
  "inputs": {
    "config.json": {
      "bytes": 174,
      "sha256": "caa99cfabb254a62ef7896ecfe0fe0cb913c66822a02eea170d73fe33230f9ba"
    },
    "drift.py": {
      "bytes": 1525,
      "sha256": "55d2ead535ed2a02ffe4e9b7489309c8375be8c424f973fdc1cd017e366bc03d"
    }
  },
  "invariants": {
    "robust": true
  },
  "kind": "experiment",
  "source": "auditor",
  "status": "Deviated",
  "title": "Drift route: improved metric with contradictory mechanism",
  "updated_at": "2026-10-09T02:21:17.597605+00:00",
  "version": 4
}
````
