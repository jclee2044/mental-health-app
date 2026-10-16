# Curated design evidence log

## Repository publication preparation — October 15, 2026

The user requested ignoring `report.md`, checking for API keys or similar secrets, and committing/pushing the project. The report remains a local file; links to it in repository documentation therefore refer to a separately supplied submission draft. `.gitignore` also excludes common private-key and credential-file names. Candidate text files were scanned for provider tokens, private-key headers, credential URLs, assigned secrets, JWTs, and high-entropy literals outside lockfile integrity hashes. No findings were returned. The mockup was visually reviewed for credentials; no visible credentials were found. Pattern scanning is limited and cannot prove the absence of all secrets.

Commands/checks: `git status`, `git remote -v`, `git ls-files --others --exclude-standard`, `git check-ignore`, project-owned Python scanning, source/document inspection, and the local image viewer. The user supplied the missing Git author identity and explicitly authorized the initial commit and push. Only local Git identity is configured. The intended commit contains the scaffold, manifests/lockfile, documentation, handoff, and mockup; the report, environments, dependencies, builds, caches, and environment files are excluded. No application behavior was changed or newly tested in this publication task. Commit/push outcome is reported in chat and must be verified against Git rather than inferred from this preparation entry.

## October 15, 2026 Part 3.1

| Evidence | Decision or result |
| --- | --- |
| User's initial concept and batched grill-me interview | Phone flow: splash, Home, log/calendar, breathing, open chat, persistent Help |
| User's follow-up answers | Required feeling/color/graph; optional text; 3–2–1 countdown; open chat; reply settings; adaptive UI unresolved; passive sensing deferred |
| Targeted follow-up answers | United States resources; pleasantness/energy axes; specific interest in fourteen Sleight of Mouth patterns |
| Revised approach: initial suggestion to replace graph with slider-only logging | User retained the separate graph; prompt preserves it and documents extra effort and possible duplicate pleasantness reporting |
| Revised approach: initial suggestion of bounded reframe chat and “Simpler view” | User chose open-ended chat and left adaptation open; docs remove those as committed features while retaining fixed steps/timing for any future guided exercise |
| Research review | Dimensional self-report, color associations, breathing, conversational CBT, CCI content, NLP evidence limits, RAG, LLM failure risks, and accessibility sources recorded in `research-notes.md` |
| Resource lookup | U.S. crisis counseling verified through local-hotline lookup; 911 emergency-services role checked through National 911 Program; design requires no real calls in demonstrations |
| Source access limitation | NEJM AI full-text request failed and PMC breathing full text returned a browser challenge. No Therabot findings were used; breathing claims are limited to the accessible PubMed abstract |
| Existing source inspection | Vue retains its generated starter; no project-specific implementation created in this task |

Commands used for inspection: `pwd`, `rg --files` with generated directories excluded, `cat` for project rules/README/assignment/setup/skills/starter source, and `tail` for README's prior TODOs. File mutations use `apply_patch`. Documentation verification uses `backend/.venv/bin/python` with an inline script for local Markdown link resolution, balanced code fences, trailing newlines, R/D traceability, and confirmed prompt content. No dependencies installed, processes started, Git history changed, or external messages sent.

## Verification status

Initial documentation verification passed before the tool correction: seven Markdown deliverables checked; all thirteen local file links resolved; code fences were balanced; files had trailing newlines; all ten R/D findings had traceability entries. Manual review checked agreement between the initial prompt, README, agent rules, design choices, and source limitations. Existing setup evidence was retained. No application tests were needed for these documentation-only changes.

The user subsequently confirmed that the wireframes were created with ChatGPT's image generation tool. README, agent rules, design notes, and AI-use disclosure now reflect static generated images. The unused prototype prompt was deleted at the user's request. Image files/links, the actual generation prompt, and model/version remain to be recorded. The generated images have not been inspected here.

Correction checks use `rg` to find stale tool/file references and project-owned Python to confirm the removed prompt is absent and remaining local Markdown links resolve. Phone interaction, accessibility, animation timing, actual call-link behavior, model behavior, database persistence, and API behavior remain unverified. This is a design/documentation milestone, not a working application demonstration.

## Submission evidence still needed

- Supplied [early mockup](early-mockup.png) is embedded in the report and visually reviewed; any later behavioral walkthrough must distinguish static design from working interactions.
- Repository URL and approved commit identifying the submitted version.
- Fill the repository/commit placeholders in [the Part 3.1 report](../report.md).
- Student review of research summaries and AI-use disclosure.

## Part 1 report assembly

The user requested `report.md` with Scope and project access, Research notes, Design considerations, Flow diagram, and Early mock up, preserving as much of the user's wording as possible. The report combines the original exploration/discussion and interface descriptions with confirmed follow-up decisions. Earlier sensing/vector-storage ideas are retained as earlier considerations, while current scope, evidence limits, and unresolved privacy choices remain explicit.

The initial report contained a detailed Mermaid flowchart of the three activities, exit/pause paths, secondary preferences/history, and an independent Help branch applying to every screen. Static wireframe placeholders do not assert that images have been inspected. README links the report and AI-USE records assistance with its assembly and diagram.

Inspection used `cat` and `rg --files`; edits used `apply_patch`. Verification uses `backend/.venv/bin/python` for local links, required report sections, explicit placeholders, balanced fences, and the diagram's node/edge references. No new application checks, dependencies, processes, or Git changes are part of this documentation task. Mermaid rendering and the actual wireframe images still require visual review.

Passed: all five requested report sections and repository/commit/image placeholders are present; all twenty-two local links across the report and existing documentation resolve; code fences are balanced; all edges reference defined nodes in the twenty-one-node flowchart. These structural checks do not verify Mermaid rendering or application behavior.

## Report revision for length and voice

The user requested roughly half the length, approximately 75% user wording/content with AI support matching their tone, fewer sections, a simpler diagram, no mockup table, and a list of actual unresolved questions. The report was reduced from 4,076 to 2,198 whitespace-separated words (about 54% of its earlier length). Feature descriptions now sit together in Scope, the flowchart has nine nodes, and the NLP evidence paragraph was removed as requested. The questions retain the user's uncertainty about affective/adaptive UI, anxiety and stress tracking, individual baselines, and other unresolved design details.

Changes affect `report.md`, `AI-USE.md`, and this evidence log. Inspection used `cat` and `sed`; editing used a shell heredoc and `apply_patch`; checks used project-owned Python for word count, sections, local links, diagram references, placeholders, and absence of the removed paragraph/table. No application behavior or image rendering was checked.

## Mockup linkage and current handoff

The user supplied `docs/early-mockup.png`, requested it be linked in the report, removed five specific open questions and the closing submission-reminder paragraph, and requested 65–80% of the previous report length. The updated report is 1,619 whitespace-separated words, 73.7% of the preceding 2,198-word draft. The simple flow, research references, all ten assignment findings, five remaining questions, and repository/commit placeholders are retained.

The image was opened with the local image viewer and visually inspected. It depicts the main activities and secondary screens. Its Help panel still uses a pending-country/number placeholder and its graph calls the axes provisional; confirmed U.S. resources and pleasantness/energy axes remain the design decisions. The image itself was not edited. Static review does not establish interaction behavior.

The previously empty handoffs directory now contains [current.md](../handoffs/current.md), covering current status, user writing preferences, confirmed scope, image observations, unresolved implementation details, and verification boundaries. README, agent rules, design notes, and AI-use disclosure now link or identify the supplied image rather than saying it is missing.

Inspection commands: `cat`, `rg --files`, `rg -n`, and `ls -la handoffs`; file changes used a shell heredoc and `apply_patch`. Project-owned Python verifies length, sections, questions, removed text, R/D rows, PNG signature/dimensions, and local Markdown references. Application behavior and Mermaid rendering are not verified in this update.
