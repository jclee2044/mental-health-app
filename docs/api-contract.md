# JSON API contracts

The shared request/error boundary is described in [architecture](architecture.md). Each feature owns its endpoint shapes and storage decisions:

- [Emotion entries](../backend/app/features/emotion/CONTRACT.md): explicit choices, calendar/history, edit/delete, safe retry.
- Guided breathing: `backend/app/features/breathing/CONTRACT.md` is added with the breathing module.

All API routes use JSON and `Cache-Control: no-store`. No personal response is cached by the PWA. Same-origin development uses Vite’s `/api` proxy; the production build is served by FastAPI on localhost.
