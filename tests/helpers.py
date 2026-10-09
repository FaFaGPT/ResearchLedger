import json
import shutil
from pathlib import Path
from researchledger.engine import Ledger

REPO = Path(__file__).resolve().parents[1]


def setup_project(root):
    root = Path(root)
    for name in ("experiment.py", "config.json"):
        shutil.copyfile(str(REPO / "examples/robust-location" / name), str(root / name))
    ledger = Ledger(root)
    ledger.init("Test robust location estimation")
    data = json.loads((REPO / "examples/robust-location/innovation.json").read_text())
    inv = ledger.add_innovation(data)
    inv = ledger.evolve(inv["id"], "approve", "Authorized toy research")
    return ledger, inv


def contract(inv):
    return {"title": "Median vs mean", "innovation_id": inv["id"], "hypothesis": "Median lowers MSE under contamination",
            "purpose": "Test outlier robustness", "algorithm": "median-vs-mean", "model": "location-estimator",
            "dataset": "synthetic-contamination-v1", "metric": "mse", "seeds": [11, 22, 33],
            "config": "config.json", "code": ["experiment.py"], "command": ["{python}", "experiment.py"],
            "allowed_changes": [], "forbidden_changes": ["config.json", "experiment.py"],
            "acceptance": {"direction": "minimize", "min_delta": 0.5, "min_pairs": 3},
            "budget": {"max_seconds": 10, "max_output_bytes": 65536}, "stop_conditions": ["wall-time budget", "output budget"],
            "evaluation": "100 paired contaminated samples per seed", "data_processing": "Seeded Gaussian samples plus two +20 outliers",
            "training": "No learned parameters; deterministic estimator"}
