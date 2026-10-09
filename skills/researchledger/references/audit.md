# Evidence protocol and interpretation

Result JSON contains exactly `observed` and `trials`. `observed` reports actual model, dataset, algorithm, metric, seeds and innovation invariants. Trials contain:

```json
{"seed": 11, "variant": "baseline", "value": 0.5,
 "model": "location-estimator", "dataset": "synthetic-v1", "metric": "mse",
 "evaluation": "fixed held-out protocol", "compute_budget": 100}
```

For each declared seed, include exactly one baseline and one treatment trial. Values must be finite; paired model, dataset, metric, evaluation protocol and compute budgets must match the contract/each other. V1 supports one primary scalar metric per contract. Raw result bytes and logs are stored before inspection. An improved mean paired delta is separate from acceptance (direction, minimum delta, minimum pairs). These checks do not establish statistical significance, external validity or absence of leakage.

| Status | Meaning |
| --- | --- |
| Completed | Execution succeeded and implemented structural checks passed |
| Failed | Nonzero exit, timeout, output limit or other observed stop |
| Deviated | Detected unauthorized file/config/report change, unfair comparison or innovation invariant drift |
| Unverified | Incomplete run/report, malformed data, missing evidence or broken blob integrity |

Deviation takes precedence over failure; raw execution success/failure remains available separately. A missing mechanism invariant is Unknown, not proof of compliance. A declared invariant mismatch can indicate innovation drift even when metric delta improves. The current checks cannot infer arbitrary mathematical equivalence, prove reported config was used, or detect every external side effect. Review the actual source blobs, functions, config and logs. Source function extraction is not a dynamic call trace.

Method Cards include declared scientific principles, captured source/config artifacts, function names/lines, Git commit/status, platform/Python version, argv, observed changes, declared data-processing/training/evaluation and raw evidence links. Unknown dependencies, runtime call order or unverifiable method claims stay explicitly Unknown. Git dirty state is recorded; exact declared input bytes remain preserved independently of Git.

Formal Supported/Refuted decisions require a Completed confirmatory audit, current innovation revision, intact evidence, and a nonempty researcher review artifact. Supported also requires contract acceptance. Refuted requires scientific reasoning in the review; a failed run cannot refute a hypothesis. Inconclusive decisions can preserve lessons from incomplete runs. Outcomes update hypothesis state and the innovation's derived assessment. Conflicting Supported/Refuted decisions produce Contested rather than discarding negative evidence.

Review artifacts should state which code/config/evidence was checked, what mechanism it supports, comparison fairness, uncertainty/statistics, limitations, and the researcher's authorization. The system checks the artifact exists and pins its bytes; it cannot authenticate its author or judge its reasoning.
