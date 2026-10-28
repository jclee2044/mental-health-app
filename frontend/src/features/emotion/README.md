# Emotion log module — second commit

This folder owns the graph-first one-page form, explicit personal color, draft state, saved confirmation, calendar/day views, edit/delete, endpoint wrappers and feature styles. It imports shared UI, date utilities and the HTTP client, never the breathing module. Registration is `index.js`; the shell discovers it automatically.

Backend counterpart: `backend/app/features/emotion/`. Its CONTRACT.md defines fields, responses/errors, retries, dates and deletion. Backend tests cover domain validation, idempotent saves, editing, deletion, restart persistence and storage failures. Browser checks used fictional data to save/edit/reload history and verified that a failed save preserves all inputs and leaves Emergency available.

AI use: Codex authored this module from the user's confirmed design. Tools: file/shell tools, existing Vue/FastAPI environments, pytest and CUA browser testing. No additional dependencies or live model were used. Exact served model identifier is unavailable. Earlier planning placed breathing history inside emotion history; the user requested independent commits, so it was separated to remove that dependency. Isolated checkpoint verification records the resulting behavior.

October 28 revision: the graph replaces feeling cards and the separate graph page. No visible selection summary. `graph.js` owns captured pointer placement/dragging; CSS provides 90ms tracking, disabled by shared reduced-motion rules. Optional slider controls and graph arrow keys edit the same coordinates. New feeling is null; legacy categories remain readable in history and preserved on edit. No requests occur during graph movement.
