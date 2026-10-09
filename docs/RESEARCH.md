# Prior art and primary sources

Reviewed 2026-10-09. These sources informed the implementation, rather than being dependencies.

| Source | Established capability | ResearchLedger choice |
| --- | --- | --- |
| [Codex skills](https://developers.openai.com/codex/skills) | Discoverable instructions with name/description and progressively loaded resources | Self-contained skill plus Python helpers; no AGENTS.md edits |
| [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) | Runs, parameters, code versions, metrics, artifacts | Complement run tracking with scientific intent, contracts and decisions |
| [DVC experiments](https://doc.dvc.org/user-guide/experiment-management) | Git-associated experiments, data/pipeline and metric tracking | Preserve Git provenance, leave data versioning to existing tools |
| [W&B tracking](https://docs.wandb.ai/models/track) | Experiment tracking integration target | Adapter protocol only in V1; no claim of implemented cloud integration |
| [Obsidian Bases syntax](https://help.obsidian.md/bases/syntax) | YAML-based .base files with filters, properties and views | Generate filtered table views alongside Markdown dashboards |
| [Obsidian Properties](https://help.obsidian.md/properties) | Typed frontmatter metadata | Stable IDs, versions, status, provenance and links |
| [Obsidian internal links](https://help.obsidian.md/links) | Wikilinks among notes | Vault-relative stable-ID links; no title-based renames |

ResearchLedger does not implement a training framework, artifact hosting service or data versioning engine. Existing trackers can supply evidence through an explicit normalized adapter contract. The scientific contribution and its authorization remain in the local ledger.
