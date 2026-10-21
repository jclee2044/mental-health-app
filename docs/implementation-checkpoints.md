# Three independently buildable commits

The shell discovers installed features, so each stage builds without code from later stages. Feature-owned styles, tests, API methods, domain rules and SQL are kept together. Emotion history never requests breathing records; breathing has its own session-history screen.

Exact cumulative scopes are in `scripts/checkpoints.json`:

| Commit | Include | Suggested message |
| --- | --- | --- |
| 1 | `interface` paths only | `feat: add responsive interface and independent emergency access` |
| 2 | `emotion` paths only | `feat: add persistent emotion logging and history` |
| 3 | `breathing` paths only | `feat: add paced breathing with synchronized animation and audio` |

The first scope includes the PWA shell infrastructure; it works without a backend using `npm run build` and `npm run preview -- --host 127.0.0.1`. The second adds shared FastAPI/SQLite/HTTP foundations alongside the first feature. The third consists entirely of its two feature folders. Existing dependencies and lockfiles are reused.

Preview a scope using `backend/.venv/bin/python scripts/stage_checkpoint.py interface` (or `emotion`, `breathing`). Add `--stage` to stage **only** those paths. The helper refuses an already populated index or an out-of-order feature commit and never commits. Inspect `git diff --cached --stat` and `git diff --cached` before committing. Do not use `git add .` or stage all of `frontend/src/features` or `backend/app/features` for the first two commits. Create commits separately after reviewing each staged scope.

Commit in the table's order. After committing interface, stage/commit emotion; then stage/commit breathing. The helper's scope is not cumulative: earlier scopes must already be committed. Verification snapshots are cumulative, so their test builds include each stage's prerequisites.

README, AI-USE, assignment/design/evidence notes already had uncommitted changes when implementation began. They are deliberately outside the scopes to avoid folding unrelated edits into the interface commit. Review those diffs separately. Feature-owned README/CONTRACT files and `docs/checkpoints/interface.md` contain stage-specific implementation disclosures and verification notes. Root documentation can be committed after those changes are reviewed.

## Verify the actual checkpoint scopes

From the repository root:

```sh
backend/.venv/bin/python scripts/verify_checkpoints.py
```

This reads `git archive` at the fixed scaffold commit in `scripts/checkpoint-base.txt`, creates ignored `.checkpoints/<run>/01-interface`, `02-emotion`, and `03-breathing` directories, and overlays only the exact cumulative scopes. It runs tests, non-mutating lint and production builds in order; backend tests start with emotion. It stops at the first failure and skips future scopes whose files are not present in a partial checkout. The fixed baseline keeps interface-only checks independent even after later commits exist. The baseline commit must be available locally (a shallow clone may need that history fetched). It never removes feature files from the live checkout, changes the Git index, creates commits or installs dependencies. It borrows the project's existing node_modules/venv; it does not establish clean-install reproducibility on another machine.

For one cumulative stage, add `--stage interface`, `--stage emotion` or `--stage breathing`. Results are saved under that run's `results.json`. Preview a snapshot using the existing Vite CLI with its frontend as the working directory. Use its backend directory with the project's absolute venv Python when testing that snapshot's API.

Before staging/committing, rerun verification if any source in a scope changes. Keep the cumulative order: interface → emotion → breathing. Optional future features should follow the same ownership boundary rather than changing earlier features.
