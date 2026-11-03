"""Best-effort local retrieval; never hold generation on unavailable memory."""
import asyncio
import sqlite3
from datetime import date
from starlette.concurrency import run_in_threadpool
from .domain import instructions


async def prepare(store, scope, query=""):
    if scope is None:
        return "", None
    try:
        preferences, context = await asyncio.wait_for(run_in_threadpool(
            store.select, date.fromisoformat(scope.local_date), scope.conversation_id, query), timeout=.2)
    except (TimeoutError, sqlite3.Error, OSError):
        return "", {"status": "unavailable", "sources": [], "emotion_summary": None}
    return instructions(context), {
        "status": "ready" if any(preferences.values()) else "off",
        "sources": context["sources"], "emotion_summary": context["emotion_summary"],
        "chat_coverage": context["chat_coverage"],
    }
