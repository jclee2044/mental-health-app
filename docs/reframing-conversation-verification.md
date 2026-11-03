# Conversational reframing and voice library verification

November 3, 2026. The user confirmed their feedback transcript was Voice and
explicitly authorized library access. The prior voice path supplied no technique
cards; a typed-only library could not establish their use in that conversation.

## Changes

- Shared delivery guidance invites a perspective conversationally; it uses a
  relevant card's operation rather than merely a positive rewrite. Quoted first-person
  lines remain available when explicitly requested. Two distinct supported angles
  are allowed when requested; one question total, with no-question/refusal/stop rules.
- Removed stale Responses wording saying no RAG source was connected.
- Voice receives all 19 active operation definitions and complete avoid-boundaries
  with source bibliography as compact labeled startup data. Seven reference-only
  entries are excluded. Source data is separate from behavioral policy; personal
  facts are never inserted into the catalogue or embedded. There are no voice
  embeddings, mid-session lookups, new tools/events, dependency or automatic restart.
- A 200ms local optional wait and 7,500-byte source/history content allocation
  protect setup. Oversize or bad-corpus cases preserve history, omit all references
  and report unavailable. Use a fresh chat to load the full catalogue. Page/section
  locators and extended notes/examples are not in the compact voice payload.
- Source availability is not a claim that a particular generated reply used a card.
  Actual operations are assessed by meaning, not by a model's self-reported label.

## Observed checks

`backend/.venv/bin/python -m pytest backend -q`: **350 passed**, one existing
Starlette/httpx deprecation warning. New tests cover exact active operations/guards/
attribution, disabled I/O, actual session payload, source-policy separation,
personal-fact separation, long-history preservation, bad-corpus fallback and
rejection of browser-supplied cards. Existing cancellation and late-session cleanup
checks pass.

`cd frontend && npm test`: **140 passed**. Tests cover report propagation into the
nonblocking notice, continued typed use and rejection of late abandoned reports.
Oxlint, ESLint and frontend production build passed; the existing bundle-size
warning remains. The last test addition changes tests only.

A zero-network read-only startup check using local enabled configuration confirmed
all 19 operations fit a fresh session: [readiness](reframing-voice-readiness.json).
Typed vector index/corpus files were not changed or rebuilt.

The user separately authorized **three** fictional text-only reply requests, with
**zero embeddings and no microphone**. [Observed outputs and qualitative assessments](reframing-conversation-observations.json)
record a conversational graduation perspective, two different supported angles,
and refusal with the catalogue present. All returned and met those sample expectations.
These Responses checks used the exact compact catalogue; they were not GPT-Live
sessions. The graduation theme is close to the prompt example, so the result is not
held-out validation or proof of causal reliance on source cards.

## Limits and use

Live startup acceptance, acoustics, interruption while speaking, and GPT-Live's
actual spoken delivery of the new catalogue remain unverified by these checks.
Existing sessions retain old instructions/context. After backend reload, end the
old chat and explicitly start Voice in a fresh chat; no microphone restart occurs
on its own. Longer typed-to-voice histories may omit references instead of losing
history. Typed lookup still embeds only the current typed message; generic follow-ups
can lack a matched card, even though generation has current-chat history.

Files changed for this increment: voice prompts/settings/provider/routes/schemas
and new catalogue tests; reframing catalogue module/registration/reference policy;
frontend voice/useChat/ChatView and voice/chat tests; contracts, README, AGENTS,
AI-USE and evidence notes. No new endpoint, dependency, card/index edit or commit.

API/prompt basis: [Live startup context](https://developers.openai.com/api/docs/guides/live-conversations),
[Responses delegation](https://developers.openai.com/api/docs/guides/live-delegation),
and [prompt examples/evaluation](https://developers.openai.com/api/docs/guides/prompt-engineering).


Final regression: the separate personal-memory evaluation passed all
26 scenarios again. `git diff --check` passed; the original checkpoint
manifest is unchanged. The backend started by this chat was gracefully stopped
and relaunched with the README's `uvicorn --env-file .env` command on localhost
port 8000; startup completed. No browser microphone was opened or automatically
restarted, and existing Voice sessions were not claimed to have adopted new data.
The browser-control connection was unavailable during the final UI check, so no
claim is made of observing the updated screen or spoken behavior in that browser.

Local detailed logs: `tmp/reframing-conversation/catalogue-tests.txt`,
`frontend-tests.txt`, `build.txt`, and `memory-regression.json`. Three new paid
Responses requests were authorized and consumed; no further allowance is implied.
