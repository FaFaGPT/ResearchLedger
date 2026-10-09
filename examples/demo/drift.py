"""Real CPU experiment: median versus mean under contaminated observations."""
import json
import os
import random
import statistics
from pathlib import Path


def estimate_location(samples, robust):
    return statistics.median(samples) if robust else statistics.mean(samples)


def evaluate(seed, robust):
    rng = random.Random(seed)
    squared_errors = []
    for _ in range(100):
        clean = [rng.gauss(0, 1) for _ in range(21)]
        contaminated = clean + [20.0, 20.0]
        prediction = estimate_location(contaminated, robust)
        squared_errors.append(prediction ** 2)
    return statistics.mean(squared_errors)


def main():
    config = json.loads(Path(os.environ["RESEARCHLEDGER_CONFIG"]).read_text(encoding="utf-8"))
    trials = []
    for seed in config["seeds"]:
        for variant in ("baseline", "treatment"):
            trials.append({"seed": seed, "variant": variant,
                           "value": evaluate(seed, variant == "treatment" and config["robust"]),
                           "model": config["model"], "dataset": config["dataset"], "metric": config["metric"],
                           "evaluation": "100 paired contaminated samples per seed", "compute_budget": 100})
    Path(os.environ["RESEARCHLEDGER_RESULT"]).write_text(json.dumps({"observed": dict(config, robust=False), "trials": trials}, allow_nan=False), encoding="utf-8")
    print("Evaluated %d paired seeds" % len(config["seeds"]))


if __name__ == "__main__":
    main()
