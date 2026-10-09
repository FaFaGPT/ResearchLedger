# Optional Obsidian view

```text
obsidian init /path/to/existing-vault
obsidian init vault --namespace ResearchLedger-MyStudy
obsidian status
obsidian sync
```

A relative vault path is resolved against the project. Init records a new connection and reserves a dedicated namespace; it does not install Obsidian, edit `.obsidian/` settings or migrate existing notes. Open the vault folder in Obsidian and navigate to `<namespace>/Dashboard.md`. Native Properties, Bases and Graph expose relationships. `Research.base` provides Innovations, Experiments, Decisions and Evidence table views. Markdown navigation works without Bases.

The export includes stable ID notes, methods, audits, decisions, literature, compact state, raw evidence and captured source files. Sync therefore intentionally copies those materials to the selected vault; choose a suitable vault for private research. Do not put credentials in experimental config or output. Review before sharing a vault.

Existing literature notes can be registered with `literature "Paper title" "note:Reading/Paper.md" --innovations INN-ID`. They must already exist in the connected vault, and are linked without being managed. URL/DOI locators are also preserved as text. `obsidian candidate Ideas/New-method.md` captures a note as PendingReview; it never changes the official innovation registry. After reviewing its content, explicitly create an AI-Proposed or Researcher-Proposed innovation with the appropriate authorization.

Sync preflights every generated path and rejects traversal, absolute generated paths, symbolic links, Windows reparse points and unsafe filenames. Ownership is established only by the export manifest. Existing unmanaged files, edited generated files and file/directory collisions stop sync before ordinary writes. Unchanged files keep their modification times. A two-phase manifest supports retries after interrupted writes. No deletion or force-overwrite mode exists. Move your edits into separate personal notes or choose a new project namespace; never discard edits merely to clear an error.

Concurrent adversarial filesystem mutation is outside the threat model. Pause edits to generated notes while syncing; a just-before-write recheck catches ordinary races but does not provide a transactional filesystem across an entire vault. If a journal write succeeds and cache refresh fails, replay the journal; caches are not authoritative.
