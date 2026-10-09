"""Dependency-free runtime validators. JSON is the authoritative interchange format."""
import math
from .store import LedgerError, relative


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def fields(data, required, optional=()):
    require(isinstance(data, dict), "Expected an object")
    require(not (set(required) - set(data)), "Missing fields: " + ", ".join(sorted(set(required) - set(data))))
    require(not (set(data) - set(required) - set(optional)), "Unknown fields: " + ", ".join(sorted(set(data) - set(required) - set(optional))))


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 16000, name + " must be nonempty text (max 16000 chars)")


def number(value, name, positive=False):
    require(type(value) in (int, float) and math.isfinite(value), name + " must be finite numeric data")
    if positive:
        require(value > 0, name + " must be positive")


def strings(value, name, nonempty=True):
    require(isinstance(value, list) and (bool(value) or not nonempty), name + " must be a list")
    for item in value:
        text(item, name)
    require(len(set(value)) == len(value), name + " has duplicates")


def innovation(data):
    fields(data, ("title", "motivation", "mechanism", "contribution", "origin", "invariants"), ("literature",))
    for key in ("title", "motivation", "mechanism", "contribution"):
        text(data[key], key)
    require(data["origin"] in ("Researcher-Defined", "Researcher-Proposed", "AI-Proposed"), "Invalid innovation origin")
    require(isinstance(data["invariants"], dict) and data["invariants"], "invariants must map config keys to expected values")
    for key in data["invariants"]:
        text(key, "invariant key")


def contract(data):
    fields(data, ("title", "innovation_id", "hypothesis", "purpose", "algorithm", "model", "dataset", "metric", "seeds",
                  "config", "code", "command", "allowed_changes", "forbidden_changes", "acceptance", "budget", "stop_conditions", "evaluation", "data_processing", "training"),
           ("replication_of", "replication_reason", "exploratory"))
    for key in ("title", "innovation_id", "hypothesis", "purpose", "algorithm", "model", "dataset", "metric", "evaluation", "data_processing", "training"):
        text(data[key], key)
    require(isinstance(data["seeds"], list) and data["seeds"] and all(type(x) is int for x in data["seeds"]), "seeds must be nonempty integers")
    require(len(set(data["seeds"])) == len(data["seeds"]), "Duplicate seeds")
    relative(data["config"])
    for key in ("code", "command", "allowed_changes", "forbidden_changes", "stop_conditions"):
        strings(data[key], key, nonempty=key not in ("allowed_changes", "forbidden_changes"))
    for path in data["code"] + data["allowed_changes"] + data["forbidden_changes"]:
        relative(path)
        require(path.split("/")[0] not in (".research", ".git"), "Internal ledger/Git paths cannot be experiment scope")
    require(data["config"].split("/")[0] not in (".research", ".git"), "Internal configuration path forbidden")
    fields(data["acceptance"], ("direction", "min_delta", "min_pairs"))
    require(data["acceptance"]["direction"] in ("maximize", "minimize"), "Invalid metric direction")
    number(data["acceptance"]["min_delta"], "min_delta")
    require(data["acceptance"]["min_delta"] >= 0, "min_delta cannot be negative")
    pairs = data["acceptance"]["min_pairs"]
    require(type(pairs) is int and 1 <= pairs <= len(data["seeds"]), "Invalid min_pairs")
    fields(data["budget"], ("max_seconds", "max_output_bytes"))
    number(data["budget"]["max_seconds"], "max_seconds", True)
    require(type(data["budget"]["max_output_bytes"]) is int and 1024 <= data["budget"]["max_output_bytes"] <= 16 * 1024 * 1024, "Output budget must be 1 KiB to 16 MiB")
    require(type(data.get("exploratory", False)) is bool, "exploratory must be boolean")
