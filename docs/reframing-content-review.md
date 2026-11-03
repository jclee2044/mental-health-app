# Reframing source review and implementation recommendation

Reviewed November 2, 2026. This is a content and application-design review of the
three supplied books. It recommends a versioned library of technique cards with
vector search, linked supporting notes, and a separate server-owned conversation
policy. No knowledge-base ingestion, embeddings, model requests, application
changes, or guided reframing exercises have been implemented by this review.

## Sources and review coverage

The EPUB and PDFs remain in the user's Downloads folder. Full book text and
page images are not included in this document or intended for the public
repository. References below identify source sections, PDF page positions and,
where checked, printed page numbers. PDF positions are one-based. Do not apply
one offset to every page of a book: front matter, omitted blank pages and scanned
spreads make those offsets unreliable.

| ID | Supplied source | Use in this review |
| --- | --- | --- |
| D-E | Robert Dilts, *Sleight of Mouth: The Magic of Conversational Belief Change*, EPUB. Package metadata says Dilts Strategy Group, 2017-10-15, source ISBN 9781947629028, copyright 1999. | Main readable Dilts text: 95 spine entries including the cover, front matter, ten chapters, afterword, bibliography and index. References use internal XHTML locations plus section headings. |
| D-P | Same title, supplied 1999 PDF, 175 PDF pages. | Image-only scan with two printed pages on typical spreads. Used for representative text/diagram comparisons, not assumed to be identical to the digital edition throughout. |
| O | Doug O'Brien, *The User's Guide to Sleight of Mouth*, supplied 2010 PDF, 132 PDF pages. | Belief unpacking, the fourteen patterns, practice maps, worked dialogues and all five appendices. Printed page numbers match the inspected PDF positions. |
| B-G | Richard Bandler and John Grinder, *Reframing: Neuro-Linguistic Programming and the Transformation of Meaning*, supplied 1982 PDF, 208 PDF pages. | Introduction and all six chapters: meaning/context, negotiation between parts, creating a part, six-step reframing, systems and dissociated states. |

Review method: enumerate all source units; examine the chapter/section structure
throughout; read pattern definitions, the main procedure outlines, and selected
explanatory and dialogue passages closely; compare overlapping methods; inspect
representative diagrams and page renderings. Coverage is chapter-by-chapter,
not a claim of line-by-line proofreading of every paragraph, factual checking of
every anecdote, or visual verification of every figure. The scan has not received
a complete OCR or cross-edition collation.

### Extraction findings that affect implementation

- D-P has no extractable text. A local Swift/Vision OCR attempt failed on its
  first page; it did not produce a reviewed OCR corpus. The supplied EPUB
  subsequently provided readable text without requiring installation or a paid
  service.
- D-E contains only its cover image. Captions and references to diagrams survive
  in the prose, but the diagrams themselves are absent from the archive. It is
  therefore useful for text, not a complete substitute for the PDF. Visually
  checked D-P PDF pages 12, 137, 140 and 144; the latter three show printed
  256-257, 262-263 and 270-271. These checks support selected correspondence,
  not wholesale edition equivalence.
- O's pattern maps on PDF pages 79-82 have no substantive extractable diagram
  text. Page 79 was rendered and read visually. The map repeats Redefine and
  Apply to Self for different sides of a belief; repeated positions are not
  additional pattern families. Page 13's belief-structure discussion was also
  checked visually.
- B-G's text layer contains errors such as variants of the title and broken
  words. Its six-step outline at PDF page 116 / printed page 114 was checked
  against a rendering. Store corrected card text separately from original
  extraction; preserve the original locator.
- D-E's Hierarchy of Criteria procedure describes four locations but later
  refers to location 5. This procedural numbering needs a source-image check
  before any future implementation; the conversational values pattern does
  not require executing that procedure.

## What each book contributes

### Dilts

| Chapter | Material examined | Application implication |
| --- | --- | --- |
| 1, Language and Experience | Language framing, map/experience distinction, connective words and the short "even though" exercise. | Separate reported events from their interpretations; preserve the person's meaning rather than substitute a stock phrase. |
| 2, Frames and Reframing | Outcome and feedback frames; changes of frame size; context/content reframing; critics, intention, redefining and another person's perspective. | Provides foundations and several card families. Distinguish a user's goal from one chosen by the assistant. |
| 3, Chunking | More specific details, broader categories, analogies, isomorphism exercises and repunctuation. | Index the operation on meaning as well as the topic. Chunk up and chunk down have different jobs. |
| 4, Values and Criteria | Values versus evidence/criteria; chains; reality strategies; hierarchies; spatial exercises. | Values must come from the user. A short values question is different from the spatial/imagery procedures described in the chapter. |
| 5, Beliefs and Expectations | Generalizations about possibility, capability and deserving; expectations, consequences, belief assessment and "as if" work. | Useful distinctions for understanding an explicitly expressed concern; not automatic labels or a required assessment questionnaire. |
| 6, Basic Structure of Beliefs | Meaning/equivalence and cause-effect relations; values/belief audits; counterexamples. | Add optional relation metadata and clarifying questions. Do not manufacture missing causes or meanings. |
| 7, Internal States and Natural Belief Change | Belief-change cycle, states, anchoring, mentors, spatial procedures and chaining. | Keep extended procedures outside ordinary chat retrieval. The app does not observe or verify bodily state changes. |
| 8, Meta Structure of Beliefs | Presuppositions, self-reference, logical levels, Apply to Self and Meta Frame. | Preserve self-directed inquiry variants; do not adopt coercive presuppositions or assert hidden motives. |
| 9, Applying the Patterns as a System | All fourteen definitions, related questions, worked applications and adversarial demonstrations. | Best canonical taxonomy source. The system is a repertoire, not fourteen steps to run on someone. |
| 10, Conclusion | Recap of framing, belief structure and flexible application. | Supports organizing the library around relationships between techniques rather than isolated canned replies. |

Key locators in D-E: `OEBPS/Text/part0018.xhtml` (context),
`part0019.xhtml` (content), `part0021.xhtml` (intention/redefining),
`part0025.xhtml` through `part0030.xhtml` (chunking),
`part0037.xhtml` and `part0038.xhtml` (reality strategies),
`part0039.xhtml` and `part0040.xhtml` (criteria),
`part0053.xhtml` through `part0062.xhtml` (belief structure and counterexamples),
`part0064.xhtml` through `part0071.xhtml` (belief change and nonverbal work),
`part0074.xhtml` through `part0081.xhtml` (presuppositions/self-reference/levels),
and `part0083.xhtml` through `part0089.xhtml` (definitions and application).
Afterword, bibliography and index were inspected as reference material, not
runtime technique instructions.

### O'Brien

| Section | Material examined | Application implication |
| --- | --- | --- |
| Part One, PDF pp. 4-31 | Perception/interpretation; compressed belief statements; unpacking; normalized cause-effect-meaning structure; pattern maps. | Often the useful next move is clarification. Do not assume the user has supplied the whole relation just because a topic matches a card. |
| Part Two, pp. 32-77 | Choosing an outcome; three learning groups covering all fourteen patterns; examples; memory/visualization drills. | The learning groups are not execution order. Outcome direction must remain user-owned; learner drills do not belong in user conversations. |
| Maps and dialogues, pp. 78-92 | Repeated examples across patterns; organization coaching; a role-played relationship conversation. | Extract technique distinctions and write original fictional examples; avoid treating a transcript's complete strategy as the default chat policy. |
| Mastery/history, pp. 93-100 | Practice, teaching stories and origins of the pattern map. | Reference-only learning material; no compulsory visualization or continuous pattern chaining in chat. |
| Appendix 1, pp. 101-105 | Agreement frame and delivery. | Acknowledge accurately; never manufacture agreement to obtain compliance. |
| Appendix 2, pp. 106-115 | Precision/Meta Model questions and a physical memorization exercise. | Candidate clarification cards: specifics, comparisons, universals and constraints. The finger-anchoring exercise is separate. |
| Appendix 3, pp. 116-124 | Plausibility, consequences, preconditions, analogy, alternatives and comparison with chance. | Keep possibility and proof distinct; do not mistake a plausible alternative for a fact about the user's life. |
| Appendix 4, pp. 125-126 | Meaning, causes, comparisons and logical-level strategies. | Useful retrieval tags that describe the intended operation. |
| Appendix 5, pp. 127-130 | Identity, values, capabilities, behavior and environment. | Distinguish an event/action from a whole-person judgment without denying experiences or symptoms. |

Acknowledgments and author material, pp. 131-132, are attribution rather than
chat instructions.

Important differences from D-E must survive curation:

- O's **Chunk Up / Exaggerate** (pp. 54-55) reduces one side of a statement and
  exaggerates the other. D-E's **Chunking Up** (`part0027.xhtml`) moves to a
  broader classification. These are related presentations, not interchangeable
  instructions. Keep separate variants and provenance; the exaggeration variant
  is reference-only for this proposed ordinary-chat increment.
- O's intention discussion (pp. 61-62) includes guessing what someone intends;
  the app-compatible version asks or uses an explicitly supplied purpose.
- O's Meta Frame examples (pp. 71-72) include confident claims about the other
  person's motives. The app-compatible version invites the user's own
  reflection about a belief's context and accepts correction.
- Some dialogues deliberately stack patterns or redirect the topic to win an
  argument (for example pp. 44-45 and 74-75). These are examples to distinguish
  from the application's conversation policy, not instructions to adopt it.

### Bandler and Grinder

| Chapter and printed range from contents | Main content | Recommended handling |
| --- | --- | --- |
| I, pp. 5-43 | Meaning reframing versus context reframing; examples; choosing a form; delivery and observation. | Principal contribution to foundational cards. The distinctions at PDF pp. 16-19 are particularly useful. |
| II, pp. 45-56 | Negotiating between competing functions; agreements; consequences for other concerns. | Background for asking about competing needs. Do not literalize "parts" or execute the negotiation procedure through unrestricted chat. Outline: PDF p. 59 / printed p. 56. |
| III, pp. 57-103 | Defining an outcome, recalling resources, constructing/entering imagery, checking objections and creating/testing a part. | A distinct extended procedure, not a conversational reframe. Outline: PDF pp. 105-106 / printed pp. 102-103. |
| IV, pp. 105-141 | Six-step reframing, signals, intention, creative alternatives, responsibility and objections; practitioner demonstrations. | Do not confuse with the assignment's one-minute thought/evidence/alternative sequence. Outline: PDF pp. 116-117 / printed pp. 114-115. |
| V, pp. 143-177 | Interaction loops, intended versus received messages, couples/families and organizational context. | Supports distinguishing intention from impact and exploring user-reported context. Not a multi-party counseling capability. Outline: PDF pp. 148-149 / printed pp. 147-148. |
| VI, pp. 179-203 | Altered-state, addiction, medication-related, memory and severe-dissociation interventions. | Exclude procedures and case instructions from runtime retrieval. They require capabilities and responsibilities outside this localhost conversational increment. |

Introduction and reference/end matter were examined for framing and source
navigation. The book is a seminar-style text with lengthy dialogue, not a clean
set of independent instructions. Literal chunking can separate a provocative
demonstration from the surrounding discussion. Examples concerning danger,
medical care, bodily responses, touch, memory construction or overriding
resistance do not become app actions merely because a passage is retrieved.

## Recommended card catalogue

Start with fourteen canonical pattern-family cards, drawing the primary names
from D-E's `part0083.xhtml`. Attach source-specific variants instead of creating
one duplicate card per book. Add a small supporting set for meaning/context,
event-versus-interpretation, clarification and identity-versus-action. Final
supporting-card count belongs to authoring, not an invented requirement.

The middle column below is an **application adaptation**, not a claim that the
authors use exactly this wording. Runtime eligibility is approved per variant;
the catalogue can retain reference-only variants without exposing them to chat.

| Pattern family | Conversational operation and boundary | Supporting source locators |
| --- | --- | --- |
| Intention / Intent | Explore what a thought or response is trying to accomplish, without assuming a motive or excusing harmful conduct. | D-E `part0021.xhtml`; O pp. 61-62. |
| Redefining / Redefine | Offer a nearby description the user can accept, reject or correct; preserve facts, accountability and the strength of the experience. | D-E `part0021.xhtml`, `part0022.xhtml`; O pp. 47-49. |
| Consequence | Explore what holding or acting on a thought leads to; no threats, guilt or claims that beliefs cause illness. | D-E `part0046.xhtml`; O pp. 41-42. |
| Chunk Down | Clarify a specific event, detail or manageable component; avoid a barrage of questions. | D-E `part0026.xhtml`; O pp. 52-54. |
| Chunk Up | Explore a broader category or purpose; avoid exaggerating the user's view into an absurdity. | D-E `part0027.xhtml`; compare O pp. 54-55 as a separate variant. |
| Analogy / Metaphor | Offer a brief comparison, invite fit and retain the real situation's differences; analogy does not establish facts. | D-E `part0028.xhtml`, `part0029.xhtml`; O pp. 45-46. |
| Change Frame Size | Explore a different time/scope while retaining the present experience; no minimizing through comparisons with others' suffering. | D-E `part0017.xhtml`; O pp. 70-71. |
| Another Outcome | Explore a different goal only within the user's request; no strategic topic diversion. | D-E `part0015.xhtml`; O pp. 44-45. |
| Model of the World | Consider another possible perspective without claiming to know another person's mind. | D-E `part0023.xhtml`; O pp. 62-63. |
| Reality Strategy | Ask what observations support a conclusion and what remains uncertain; exclude memory/fantasy-conversion exercises. | D-E `part0037.xhtml`, `part0038.xhtml`; O pp. 65-66. |
| Counter Example | Invite a relevant exception from the user's own experience; absence of an exception is an acceptable answer. | D-E `part0060.xhtml` through `part0062.xhtml`; O pp. 56-57. |
| Hierarchy of Criteria | Explore priorities the user actually endorses; do not exploit a value to overcome refusal. | D-E `part0039.xhtml`, `part0040.xhtml`; O pp. 37-40. |
| Apply to Self | Optional, plain self-reference about a rule, never a gotcha, pun attack or reversal of blame. Skip when it would confuse or shame. | D-E `part0078.xhtml`; O pp. 67-69. |
| Meta Frame | Invite the user's own account of the context in which a belief developed; do not assert hidden causes or motives. | D-E `part0079.xhtml`; O pp. 71-72. |

Clarification is a valid result. A message can express a preference, realistic
constraint or request for acknowledgment without being a belief to change.
The pattern map is not a required progression. Success is relevant,
user-controlled conversation, not an agreement to adopt a replacement belief.

## Architecture decision

### Three layers

1. **Server-owned conversation policy:** keep listening, permission, stopping,
   factual grounding, the reflection-question rule and application boundaries
   here. Add concise rules for using retrieved cards; do not paste whole books
   into the prompt. Retrieved text is reference data, never policy authority.
2. **Reviewed runtime library:** vector-search approved card variants and their
   original fictional retrieval examples. Fetch linked, approved supporting
   notes only after selecting a relevant card. Use original summaries and
   narrowly selected passages where their use is appropriate.
3. **Private source archive and review catalogue:** retain locators, edition
   identifiers, file hashes and review decisions. Whole-book text, unreviewed
   procedures, worksheets, adversarial examples and excluded variants are not
   an automatically searchable fallback for the chatbot.

This is a more specific recommendation than automatically splitting all three
books into similarly sized chunks. Their overlap, diagrams, variants and
procedural content justify **card-first retrieval with linked context**.

### Card records and search records

Store editable, versioned card records as project JSON when authoring begins.
The schema should distinguish the pattern family, an approved variant and the
search examples that point to it. Suggested fields:

- Stable card/variant IDs, revision, title, aliases and relations to other cards.
- Original explanation of the operation; fit conditions; reasons to clarify or
  skip; non-permitted uses; interaction type (`conversation` or `procedure`).
- A few original fictional user expressions plus examples of suitable replies
  and unsuitable replies. Mark examples as synthetic; never imply they came
  from a user's history.
- Source ID/edition, EPUB href and section, or PDF position and printed page
  where verified. An adaptation note separates author definitions from app rules.
- Review/eligibility status. A reference-only record is excluded before ranking
  and linked-note expansion, not merely accompanied by a warning afterward.
- For each search representation: content hash, embedding provider/model,
  dimension, normalization convention and build revision. Reject incompatible
  vectors or stale index builds explicitly.

Do not embed only names such as "Counter Example." Embed what the method does,
when it fits and ordinary-language examples. A small number of separate example
vectors may point to one card. Deduplicate by card family so a pattern with more
examples or two source books does not consume the entire result set.

### Vector storage

Use real embeddings and vector similarity from the start, as the user requested.
For a small curated library, store vectors and metadata in SQLite and perform
exact cosine scoring in framework-free Python. This is a proposed initial
implementation, not a measured performance result or a claim that SQLite itself
performs native vector search. A dedicated vector server/extension is not needed
to implement that algorithm and would add an unnecessary service/dependency now.

The [official OpenAI embedding guide](https://developers.openai.com/api/docs/guides/embeddings)
describes querying embeddings by cosine similarity. It recommends a vector
database for searching many vectors quickly. Whether a dedicated index helps
this catalogue should be determined by measured size/latency, rather than by
the size of the original PDF files.

Keep an embedding-provider interface. OpenAI embeddings are a practical candidate
given the existing provider integration, but provider/model/dimension and where
queries are embedded must be resolved with the other user-context chat before
implementation. Hosted query embedding transmits query text and adds API usage;
local SQLite storage does not make that processing local. No embeddings were
created and no provider/account access was checked during this review.

### Per-turn behavior

Use the current message and only necessary, bounded current-chat context to
retrieve approved material. Do not turn retrieval into a persistent analysis
of the person. For greetings, direct factual questions, listening-only requests,
refusal, stopping or urgent situations, no reframe may be the correct result.
These judgments and source selection are imperfect; they require evaluation,
not an assurance from the prompt.

Where retrieval is appropriate: embed the bounded query, score eligible variants,
deduplicate candidates, select a small relevant set and attach bounded approved
notes. The model may clarify or skip instead of using a candidate. The number
of candidates, inclusion threshold, note length and context budget are tuning
parameters to validate; no arbitrary similarity value is established as correct.
Keep a no-match outcome. Never use similarity as a diagnosis or a confidence
score about a person's belief.

Retrieval supplies options; it does not supply consent. Current prompts require
asking and waiting before a deliberate reframe unless specifically requested.
That remains the proposed behavior unless the user deliberately changes it.
Corrections, no-questions requests, refusal and stopping override pattern use.
Do not chain techniques to overcome an objection. Emergency stays app-owned.

If embedding/search is unavailable, continue ordinary chat without claiming
source-backed reframing; make the knowledge-base failure visible and retryable.
Do not silently fall back to unrestricted book chunks, invent a retrieved source,
or make storage Retry regenerate a model answer.

### Fit with the existing code

Put future knowledge-base domain/retrieval/storage code in an independently
owned backend feature, following the existing feature registration structure.
Keep routes/schemas separate from framework-free rules. A backend composition
service can coordinate retrieval and the existing typed provider; the voice
feature should not become the entire knowledge-base implementation. No new
browser-facing search endpoint is necessary just to supply typed model context.
Any future API additions need the project's request/response/error contract.

Begin with typed chat. `voice/provider.py` currently creates its Responses input
on each typed turn, so the server has a natural point to supply bounded reference
context separately from the user/history. Do not simply append book text as
high-priority instructions. Model-returned source identifiers, if exposed, must
be checked against the references actually supplied; never accept invented IDs.
Retrieval metadata must remain separate from the existing saved conversation text.

Live voice has a different boundary: `voice/settings.py` sends session-owned
instructions with empty delegated tools, while browser allowlists contain only
the currently approved transcript/lifecycle events and close action. Injecting
cards at session creation would provide a fixed snapshot, not fresh per-turn
retrieval. Dynamic spoken retrieval needs a separately verified server integration
and an explicit transport/contract increment. Do not expand browser event or
provider-tool permissions as an incidental part of this content work.

### Coordination with the user knowledge base

The two libraries can share an embedding/retrieval abstraction; they must not
share eligibility rules or treat source types as interchangeable. Reframing
cards describe methods. User context describes user-reported information and
requires its own explicit inclusion choices, provenance, corrections and deletion.

Keep source collections separate and distinguish them in supplied model context.
Deletion must remove a user record's embeddings and cached retrieval copies as
well as its displayed text. Corrections need to invalidate old vectors. Personal
context must never be copied into the curated technique library, synthetic
examples or public evaluation logs. Agree on the embedding interface and revision
format before either chat builds shared infrastructure; identical model/dimension
is essential whenever vectors are compared directly.

## Authoring and verification plan

1. Author and review fourteen family cards plus the supporting cards. Resolve
   variant eligibility, source locators and original fictional examples. Keep
   full PDFs/EPUB and derived extraction outside committed corpus content.
2. Agree on embedding provider/model/dimension, query transmission and limits
   with the user-context work. Build a versioned index without personal history.
   Explain any proposed dependency before adding it.
3. Check deterministic filters, parent-note eligibility, deduplication, stale
   vectors, no-match and failure behavior using mocked embeddings/provider calls.
   These checks cannot establish actual semantic retrieval quality.
4. Run a small separately authorized embedding evaluation on fictional
   paraphrases, with expected acceptable pattern sets and reasonable no-match
   cases. Inspect misses before setting thresholds. Distinguish it from reply
   generation tests.
5. Integrate typed context and evaluate the assignment's fifteen fictional
   scenarios and three cross-case behavior checks. Preserve permission, stop,
   Emergency, context bounds and storage-only Retry. Use mocks for routine/peer
   checks, and separately authorized bounded live cases for generated behavior.
6. Evaluate dynamic Live integration separately; never describe a startup-only
   snapshot as ongoing retrieval. New guided exercises require application-owned
   steps/exits and the assignment's timing verification.

Suggested fictional semantic checks include self-judgment after one assignment,
an unreturned message interpreted as rejection, an explicit request for another
perspective, a realistic scheduling constraint, listening without advice,
correction of an inferred meaning, "no questions," refusal after an offer,
stopping, repeated requests for certainty, a request to influence somebody else,
a request for an extended book procedure, an unrelated factual question, urgent
input and an embedding failure. Expected techniques can overlap; matching one
specific card is not the only valid retrieval outcome.

Three cross-case invariants: (1) no deliberate reframe after refusal/stopping or
without the required permission; (2) only eligible, current source variants and
notes enter model context; (3) Emergency/navigation and retryable storage remain
independent of embedding and generation success. Expected and observed results
must remain separate; this review has not run those behavior checks.

## Remaining decisions

- TODO: author actual card records and check every runtime-bound locator and
  example against the source; this review is not an approved production corpus.
- TODO: agree on shared embedding configuration, transmission, cost limits and
  implementation ownership with the user-context work.
- TODO: record source-use permissions for any excerpts before corpus publication
  or external source upload. File possession does not establish redistribution
  permission. Original explanations and locators are the proposed default.
- TODO: verify diagrams/procedural numbering individually if any excluded
  procedure is later proposed. Do not reconstruct missing steps from memory.
- TODO: decide how much retrieval provenance should be visible in the app.
  Ordinary replies need not name patterns or turn into textbook explanations.
- TODO: measure actual retrieval and generated reply quality; neither has been
  established by extraction, this review or mocked application checks.

## Review provenance

Source SHA-256 values, identifying the exact supplied files:

| Source | SHA-256 |
| --- | --- |
| D-E | `ecde354ae9adc07839625d5c0cca1a0675b98635a9f4120a8b473a79693fad4a` |
| D-P | `5ce40a638a8ff5a55d80648f10a4e14b462a44dbe505434298bf23e7998bf647` |
| O | `2d8598252fc24f852041f801ba7c831868720c0798c582a704a5cdff139e14d1` |
| B-G | `7e6ac533df78565efc32a5757f8bc205b1aa4e679afa143eb7dac7db4ca22963` |

Tools: existing Python/pypdf for extraction and metadata; Python zipfile/XML for
EPUB structure/text; pdfinfo/pdftoppm and image inspection for PDF checks; local
Swift/PDFKit/Vision for the failed OCR attempt; read-only repository inspection;
official OpenAI documentation for embedding mechanics. Temporary extraction,
renderings and compiler cache are private ignored working files under
`tmp/pdfs/reframing-review/`. No project dependency was added. No app tests were
rerun for this documentation-only review; no paid calls, microphone use, app
runtime changes, staging or commits occurred.

## Subsequent independent implementation on November 2, 2026

After this review, the user authorized completing independent work while the
personal-memory chat continued. The card corpus, vector scoring/index, bounded
embedding adapter, offline CLI and mocked checks now exist under
`backend/app/features/reframing/`; see its contract and
[integration handoff](reframing-integration-handoff.md). The corpus has fourteen
core families, five supporting cards and seven reference-only entries. It uses
original summaries/examples and source locators rather than copied book text.

The other chat's contract now specifies **non-vector** personal memory, so a
shared embedding model is unnecessary. Its data/indexing and shared chat files
were left alone. Reframing remains disabled and disconnected from generation;
real embeddings, measured relevance/threshold and shared integration remain
pending. The earlier review's no-implementation statement describes the review
milestone, not this subsequent authorization. No paid calls were made.
