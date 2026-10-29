# Historical scaffold setup evidence

This records the October 8 scaffold and later initial-Git checkpoint, not the
current application. Statements about missing features and tracked reports below
apply to those historical checks. Use the [current README](../README.md) for
implementation, setup and verification. No historical check was rerun for this
archive.

## October 8, 2026 setup evidence

Steps 1–8 of the setup guide are complete. The user approved the current generator's bundled Oxlint on October 8, 2026. Step 9 was subsequently completed with user authorization on October 15; see the Git checkpoint below.

### Read-only preflight and tool checkpoints

The preflight was run after creating only `README.md`, `AGENTS.md`, and `.gitignore`; `backend/`, `frontend/`, `docs/`, `prompts/`, and `handoffs/` already existed. The preflight itself changed no files or environments.

| Check | Preflight status | Evidence |
| --- | --- | --- |
| Operating system | Passed | macOS 26.6.2, Darwin 25.6.0, arm64 |
| Python >=3.10 available | Passed | Python 3.12.10 and 3.12.13 available; system 3.9.6 is incompatible |
| Backend environment | Missing | No `backend/.venv` existed at preflight; created in step 5 |
| FastAPI/pytest manifest | Missing | No backend manifest existed at preflight; created in step 5 |
| Node.js/npm | Passed | Default Node.js v26.6.0 and npm 11.18.0 meet Vue's requirement |
| Frontend manifest/lock/dependencies | Missing | `frontend/` was empty |
| Git installation | Passed | `/usr/bin/git`, version 2.50.1 (Apple Git-155) |
| Git repository/status | Not applicable | No enclosing repository; status/history not available |
| Inventory | Passed | Existing assignment, setup prompts, and empty backend/frontend/handoff directories reviewed |

Available Python executables on PATH were enumerated, resolved, and checked individually:

| Path | Version | Installation |
| --- | --- | --- |
| `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3` | 3.12.10 | python.org framework (alias) |
| `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12` | 3.12.10 | python.org framework |
| `/usr/local/bin/python3` | 3.12.10 | Same framework (alias) |
| `/usr/local/bin/python3.12` | 3.12.10 | Same framework (alias) |
| `/opt/homebrew/bin/python3.12` | 3.12.13 | Homebrew framework; selected for the venv |
| `/usr/bin/python3` | 3.9.6 | System interpreter; not used |

Additional PATH alternatives: `/usr/local/bin/node` v24.21.0 and `/usr/local/bin/npm` 11.19.0. The default tools were retained. These are computer-level tools, not project-owned dependencies. A fallback Git executable also appears on PATH under the Codex runtime; `/usr/bin/git` was used.

Read-only commands used: `pwd`, `ls -la`, `rg --files` (including hidden files and targeted patterns), `find docs -maxdepth 2 -type f -print`, `cat prompts/setup-prompts.md`, `cat docs/assignment-description.md`, ancestor `AGENTS.md` checks, `cat AGENTS.md README.md`, `uname -a`, `sw_vers`, `whence -a`/`whence -pa` for Python/Node/npm/Git, individual executable `--version` calls, `command -v node npm`, `git rev-parse --show-toplevel`, `git rev-parse --is-inside-work-tree`, and `git config --get user.name`, `git config --get user.email`, `git config --get-regexp '^user\.(name|email)$'`. Python inline inspection enumerated executable names on PATH and checked whether the environment, manifests, lockfile, and dependency directory existed. Git identity was unset at that preflight checkpoint; the user later supplied project-local identity for the approved initial commit. No global configuration was changed.

### Backend installation and verification

- Created `backend/.venv/` and `backend/requirements.txt`; updated this README with the setup commands above.
- Ran the documented venv creation and pip installation. The first sandboxed download failed because PyPI DNS was inaccessible; the same project-only install succeeded with approved network access. No global packages or machine-level tools were installed.
- Ran the documented import/prefix assertion, `backend/.venv/bin/python -m pip check`, `backend/.venv/bin/python -m pip show fastapi pytest`, and `backend/.venv/bin/python -m pip --disable-pip-version-check --no-cache-dir list --format=json`.
- Passed: `sys.prefix` equals the project `backend/.venv`; `sys.prefix` differs from `sys.base_prefix`; both modules import; package locations are inside the venv; pip reports no broken requirements. Only the two declared dependencies and their resolved transitive dependencies were installed.
- No backend functions, API routes, or tests were created. Backend behavior is not yet testable.

### Frontend generator inspection

Read the official Vue Quick Start and [create-vue source/usage](https://github.com/vuejs/create-vue). Ran `npm_config_cache="$PWD/.npm-cache" npm create --yes vue@latest -- --help` with approved network access; its help confirms Oxlint is always included with ESLint. Ran the same command with `--version`, and read the cached generator's package version using `node -p` (v3.24.0). The npm generator cache is project-owned and ignored. No global npm packages were installed.

### Frontend installation and verification

Ran, in order:

```sh
# From the repository root; frontend was confirmed empty first:
npm_config_cache="$PWD/.npm-cache" npm create --yes vue@latest -- frontend --eslint --bare
# From frontend/:
npm_config_cache="$PWD/../.npm-cache" npm install
npm run lint
npm run build
npm ls --depth=0
```

- Installation succeeded: 222 packages added; npm audited 223 packages and reported zero vulnerabilities at setup time. The generated lockfile is retained. No extra dependencies were manually added.
- Lint passed for both Oxlint and ESLint. The Vite production build passed, transforming 11 modules.
- Inspected the generated manifest, Vite configuration, lint configuration, starter components, and other starter files. The frontend has no project-specific interface or API requests.
- A read-only inline Node check compared manifest dependency declarations to the lockfile root, compared every installed package version with its lockfile entry, allowed absent optional platform packages, and validated the full dependency tree using `npm ls --all --json`.
- Added ignored cache/build patterns to the root `.gitignore`; no application source was manually changed.

Files/directories created: root `README.md`, `AGENTS.md`, `.gitignore`, and ignored `.npm-cache/`; `backend/requirements.txt` and ignored `backend/.venv/`; generated frontend `README.md`, `package.json`, `package-lock.json`, `index.html`, `jsconfig.json`, `vite.config.js`, `eslint.config.js`, `.oxlintrc.json`, `.editorconfig`, `.gitattributes`, `.gitignore`, `src/App.vue`, `src/main.js`, `public/favicon.ico`, `.vscode/extensions.json`, `.vscode/settings.json`, and ignored `node_modules/`, `.eslintcache`, and `dist/`. Existing assignment and setup prompt files were not modified. The README and root ignore file were updated during successive setup phases.

### Complete scaffold verification (step 8)

| Check | Result | Evidence |
| --- | --- | --- |
| Required project directories and root files | Passed | All present |
| README architecture, setup, verification, development, TODOs | Passed | Reviewed against assignment and verified commands; backend startup deferred because no module exists |
| AGENTS project, separation, permission, reporting rules | Passed | All required rules present |
| Backend interpreter ownership | Passed | `sys.executable` and `sys.prefix` belong to `backend/.venv` |
| Exact requested backend dependencies | Passed | Manifest contains only `fastapi[standard]` and `pytest` |
| Backend imports and dependency consistency | Passed | FastAPI 0.143.0, pytest 9.1.1, `pip check` succeeds |
| Node/npm versions and paths | Passed | v26.6.0 / 11.18.0, both under `/opt/homebrew/bin` |
| Current Vue Node requirement | Passed | v26.6.0 satisfies `^22.18.0 || >=24.12.0` |
| Vue and ESLint declarations | Passed | Vue 3.5.43 and ESLint 10.12.0 installed with generated lint tooling |
| Frontend lockfile and installed tree | Passed | Lockfile v3; all 222 installed versions match; 43 optional platform packages absent as expected; full `npm ls` succeeds |
| Frontend lint | Passed | Oxlint and ESLint pass, including verification without fixes or cache writes |
| Frontend production build | Passed | Vite 8.3.4 builds successfully |
| Ignore coverage and preserved manifests/lockfile | Passed | Generated environments, dependencies, builds, caches, secrets, editors and OS artifacts ignored; declarations and lockfile visible in inventory |
| No project-specific application implementation | Passed | Backend has only its manifest; frontend has only the two generated starter source files; no API calls or custom interface |
| Backend behavior/browser interaction | Not applicable | No backend application; browser interaction outside scaffold checks and not verified |

Step 8 changed no source files, dependency declarations, or installed dependencies. Verification used the documented non-mutating lint commands, `npm run build`, `npm ls --depth=0`, `backend/.venv/bin/python -m pip --no-cache-dir check`, Node/npm version/path checks, `cat AGENTS.md`, source inspection with `cat`/`rg`, and an inline project Python assertion script checking structure, interpreter ownership, exact declarations, omitted optional features, ignore patterns, and the absence of backend application files. The build regenerated only ignored output. After verification, this README was updated with the results.

### Initial Git checkpoint (step 9)

At the original setup checkpoint, no enclosing repository existed and author identity and commit approval were pending. The user subsequently supplied identity and authorized initialization and publication on October 15, 2026, as recorded in [the evidence log](evidence-log.md).

Read-only inspection on October 21 confirms initial commit `d52a680` (`chore: initialize coursework scaffold and design documentation`), content commit `084981b`, and report-reference commit `010a9d9`. `origin` matches the repository above and `report.md` is tracked. Generated environments, dependencies, builds, caches, and secrets remain excluded. Remote availability and instructor access were not rechecked in this inspection.
