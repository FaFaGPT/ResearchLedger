---
id: "AUD-cbe6ebb7805a4df0"
type: "audit"
title: "AUD-cbe6ebb7805a4df0"
status: "Completed"
version: 1
created: "2026-10-09T02:21:17.009250+00:00"
updated: "2026-10-09T02:21:17.009250+00:00"
source: "auditor"
managed_by: "ResearchLedger"
links: ["[[ResearchLedger-Demo/Evidence/EVI-986d05356b784e5f]]", "[[ResearchLedger-Demo/Evidence/EVI-af46436803b34c35]]", "[[ResearchLedger-Demo/Experiments/EXP-e7fb59325ccf48ad]]", "[[ResearchLedger-Demo/Runs/RUN-7c62c40f281448bc]]"]
---

# AUD-cbe6ebb7805a4df0

> Generated view. Keep personal notes in separate files; manual edits here block synchronization.

## Connections
- [[ResearchLedger-Demo/Evidence/EVI-986d05356b784e5f]]
- [[ResearchLedger-Demo/Evidence/EVI-af46436803b34c35]]
- [[ResearchLedger-Demo/Experiments/EXP-e7fb59325ccf48ad]]
- [[ResearchLedger-Demo/Runs/RUN-7c62c40f281448bc]]

## Record

````json
{
  "acceptance_met": true,
  "created_at": "2026-10-09T02:21:17.009250+00:00",
  "deviations": [],
  "drift": [],
  "evidence": [
    "EVI-af46436803b34c35",
    "EVI-986d05356b784e5f"
  ],
  "execution_success": true,
  "experiment_id": "EXP-e7fb59325ccf48ad",
  "hypothesis_support": "Pending researcher review",
  "id": "AUD-cbe6ebb7805a4df0",
  "kind": "audit",
  "limitations": [
    "Observed configuration and metrics are process-reported; semantic mechanism, data leakage and external effects require review.",
    "Function extraction proves source presence, not that each function executed."
  ],
  "mean_delta": -2.9660657447821346,
  "metric_improved": true,
  "paired_seeds": 3,
  "reproducibility": "Captured inputs and paired seed report; independent rerun Unknown",
  "run_id": "RUN-7c62c40f281448bc",
  "source": "auditor",
  "status": "Completed",
  "unknown": [],
  "updated_at": "2026-10-09T02:21:17.009250+00:00",
  "version": 1
}
````
