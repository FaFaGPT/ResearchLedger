# Reproducible usage cases

Run `python tools/build_demo.py --output NEW_DIRECTORY` for real artifacts. The committed `examples/demo` is a completed instance. All evidence there is synthetic and safe for publication.

## 1. Successful execution is awaiting scientific review

The mean and median estimate a true location of zero from 21 Gaussian samples plus two +20 outliers. For each of three fixed seeds, both estimators see identical data across 100 trials. The program computes MSE directly. ResearchLedger captures its source/config, the actual result JSON and its log, then checks paired seed coverage, metrics and compute budgets. The Completed result meets the configured minimum MSE improvement.

The hypothesis remains Untested until a researcher reviews the source, comparison and limits. This avoids mistaking deterministic acceptance for novel scientific contribution. Median robustness is existing knowledge, so the innovation's stated contribution is deliberately scoped as a demonstration.

## 2. Failed route remains visible

`failure.py` raises an intentional exception. The runner records a nonzero exit and original traceback, and classifies the attempt Failed. The failed experiment remains in history and the compact resume state; it does not refute the scientific hypothesis. A retry must be an explicit new experiment or replication.

## 3. Positive metric with innovation drift

`drift.py` computes the same real paired metric but deliberately reports `robust: false`, contradicting the approved innovation invariant. The audit records both the improvement and the drift, classifies the experiment Deviated, and prevents scientific promotion. This demonstrates declarative contradiction detection, not automatic semantic understanding of arbitrary algorithms.

## 4. New Codex conversation

Run the installed Skill's `ledger.py --project NEW_DIRECTORY resume`. The goal, innovation, recent experiments, failed routes, current review task, next steps and unresolved external-validity questions come from the verified journal. A manually edited or stale STATE.md does not change the answer. Use `--details history EXP-ID` only when the underlying evidence is needed.

## 5. Obsidian navigation and personal annotations

Open `NEW_DIRECTORY/vault` as a vault. Start at `ResearchLedger-Demo/Dashboard.md`, follow an innovation to its experiments, then a method card, audit or raw evidence. Open `Research.base` for filtered tables, or Graph View for the same ID links. `Reading.md` is an unmanaged personal literature note linked by the export.

Add your annotations in separate Markdown notes. Editing a generated note intentionally causes `obsidian status` to report a conflict and prevents replacement on sync. Repeating sync without new research writes zero files and preserves timestamps.

## 6. Controlled exploration

Researcher authorization sets the innovation IDs, exact allowed change patterns, `explore/<namespace>/` branch prefix, total attempt count and wall-time reservation ceiling. After checking out an independent matching branch, an exploratory contract can execute without per-contract approval. Failed attempts still consume reservations. Strict or Bounded mode requires approved contracts. A completed exploratory run cannot support a formal conclusion; register and approve a confirmatory replication instead.
