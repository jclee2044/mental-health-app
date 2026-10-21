# Interface checkpoint

The interface owns the responsive layout, skippable entry, three independent Home choices, shared navigation, persistent Emergency access, optional appearance settings, About, a clearly unavailable chat stub, and the offline PWA shell. Feature-free builds show pending screens for emotion logging and breathing. There are no actual model messages or preloaded personal records.

Run from `frontend/`: `npm test`, `npm exec --offline -- oxlint .`, `npm exec --offline -- eslint . --no-cache`, `npm run build`, and `npm run preview -- --host 127.0.0.1`.

Observed before feature work: lint/build passed; desktop and 390px requested viewport were inspected; navigation, chat exit, Emergency resources, Escape/focus return and reduced-motion controls worked. No phone calls were placed. Later module extraction is checked again through `scripts/verify_checkpoints.py`; its per-run JSON is the observed checkpoint result. Browser PWA readiness/offline behavior and native installation are separate checks, not established by a build.

AI use: Codex (GPT-6-based agent; exact served model/version unavailable) wrote the implementation from the user's layout and behavior instructions, using the supplied ChatGPT-generated wireframe as design evidence. Sites local-preview guidance, shell/file tools, CUA browser controls and official MDN/FastAPI documentation informed implementation and checks. No new raster image model, model-service request, machine installation or additional dependency was used. Original CSS/vector/icon code supplies the visuals. Root AI-USE/evidence notes track the complete session.

The assignment requires an accurate coursework-prototype description; it appears in About rather than repeated activity-screen banners. Testing remains fictional and localhost-only. Emergency offers separately labeled U.S. crisis counseling and emergency services independently of API/model success. Link destinations are inspected without making calls; use simulated actions for demonstrations.
