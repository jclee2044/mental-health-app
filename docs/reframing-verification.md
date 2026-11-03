# Independent reframing verification

Current integration and real-model observations are in
[November 3 checkpoint evidence](reframing-implementation-evidence.md). The record
below describes the earlier independent-library milestone.

Observed November 2, 2026. This verifies an isolated backend library and its
offline tooling. It does not establish semantic matching with real embeddings,
generated reply quality, voice behavior or completed chat integration.

## Files owned by this increment

- `backend/app/features/reframing/__init__.py`, `corpus.py`, `domain.py`,
  `storage.py`, `embeddings.py`, `builder.py`, `service.py`.
- `backend/app/features/reframing/data/cards.json` and `data/scenarios.json`.
- `backend/app/features/reframing/tests/test_reframing.py`, `tests/test_cli.py`.
  Also `tests/test_builder.py` for the opt-in, request-capped export builder.
- `backend/app/features/reframing/README.md`, `CONTRACT.md`, `private/.gitignore`.
- `scripts/reframing_kb.py`.
- `docs/reframing-integration-handoff.md`, this verification record and a dated
  implementation-status addition to `docs/reframing-content-review.md`.
- Append-only entries in `AI-USE.md` and `docs/evidence-log.md`.

The shared worktree already contained the other chat's personal-memory backend,
frontend and integration changes. They were inspected for coexistence but not
edited, staged or committed here. Shared application/prompt/provider/frontend
files, root README/AGENTS and the checkpoint manifest were not edited here.

## Commands and observed results

| Command or check | Observed result |
| --- | --- |
| `backend/.venv/bin/python -m pytest -c backend/pytest.ini backend/app/features/reframing/tests -q` | Focused suite initially 46, then 56 checks passed as failure/CLI checks were added. The multiline check and four build-helper tests brought the package to **61 tests**, included in the final full run below. |
| `backend/.venv/bin/python -m pytest -c backend/pytest.ini backend/tests backend/app/features -q` | Final run: **277 passed**, one existing Starlette/httpx deprecation warning, 2.26s. Includes the personal-memory feature present in the shared checkout at that time. |
| `backend/.venv/bin/python scripts/reframing_kb.py validate` | 19 active cards, 7 reference-only cards, 76 search documents; no network. Corpus revision `2026-11-02.1`, SHA-256 `352ffd9b5d04136d2cf2759cbc6b205c89db3236f859f39a578127e6eda2b8b0`. |
| `backend/.venv/bin/python scripts/reframing_kb.py plan --output backend/app/features/reframing/private/embedding-plan.json` | Wrote the 76-document original search-text plan to ignored private working space. No vectors generated or uploaded. |
| Source-reference inspection with project-local Python | Every authored Dilts EPUB href exists in the extracted spine; PDF page references fall within the corresponding supplied document. This is a locator check, not independent verification of every paraphrase. |
| Planned scenario inspection | Fifteen unique fictional cases; every acceptable family exists among active cards. Semantic/reply results remain not run. |
| `backend/.venv/bin/python scripts/verify_checkpoints.py` | All three original cumulative scopes passed: interface, emotion and breathing. Includes each snapshot's frontend tests, lint and production build, plus backend tests for emotion/breathing. Manifest unchanged. |
| `git diff --check`, scoped source/JSON/whitespace checks and ignored-file check | Passed; generated embedding plan remains ignored. |

Checkpoint evidence is the ignored local
`.checkpoints/20261102-180950-440487/results.json`. The independent reframing
package is outside the original checkpoint scopes; the full-checkout backend
run covers it. The full current frontend suite/browser was not rerun here:
there are no frontend changes in this increment, and the other chat owns them.

## What the checks establish

- Full corpus structure, all fourteen core families, source IDs, relation IDs,
  original example shape and independent active/reference-only variants.
- Normalization, finite values, overflow handling, cosine scoring and family
  deduplication using explicitly **synthetic** vectors.
- Empty/no-match results, family exclusion and whole-card UTF-8 context budgets.
  Reference JSON contains the actual selected cards and linked bibliographic
  metadata, never a stored query or personal-memory bundle.
- Rejection of missing/extra rows, changed corpus/notes, wrong model/dimension,
  corrupt metadata/hashes/parent IDs and zero/nonfinite vectors. A high-scoring
  injected reference-only procedure makes the index unavailable before embedding
  rather than entering model context.
- Real SQLite temporary index publication and retrieval. Missing read-only
  indexes are not created; existing destination files are unchanged after a
  repeated publication attempt. Simulated publication failure leaves no partial
  destination and cleans only its own temporary build file.
- Disabled registration, literal-True permission guard and configuration/input
  failure before query transmission. The permission guard is not a classifier.
- Injected embedding HTTP success, reordered batch responses, exact outbound
  settings, invalid model/index/dimension/number/JSON/content-type/size/status
  responses, timeout and transport/provider failure. One bounded attempt,
  sanitized errors and no retry. A network tripwire blocks accidental calls.
- Offline CLI plan, import/publish, inspection, vector query, no-clobber outputs,
  project-owned output paths and stale-export rejection.
- Explicit opt-in and request-cap preflight for the prepared embedding-build
  helper, five correctly bounded synthetic batches for all 76 documents,
  export/index round-trip, immediate stop after a batch failure and no retries
  or partial output writes. No real embedding build was run.

One test-edit failure occurred while adding checks: missing-index assertions
were accidentally moved into a different test and referenced an unavailable
`tmp_path`. The failing run was 55 passed / 1 failed. The assertions were returned
to the intended test and the focused/full runs passed. No application failure
or provider request was involved.

## Not verified or activated

- No embedding model/dimension, account access or threshold is selected. No real
  corpus/query vectors were generated; no default runtime index was published.
- No paid request, microphone, live voice, generated conversation or personal
  data was used. The prepared adapter's live response naming/latency and semantic
  ranking still need authorized observation.
- Fifteen scenario expectations are planned semantic/reply checks, not generated
  evidence. Synthetic vectors demonstrate mechanics rather than language meaning.
- Shared chat integration, UI failure visibility, runtime permission decisions,
  async cancellation and startup/dynamic voice reference behavior remain in the
  integration handoff. The registered service stays off and base prompts remain
  unchanged.
- No dependencies were added, removed or upgraded. No Git staging, commit, push,
  deployment, machine installation or change to another task's process occurred.
