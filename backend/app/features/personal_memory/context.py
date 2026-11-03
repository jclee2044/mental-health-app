"""Best-effort local retrieval; never hold generation on unavailable memory."""
import asyncio
import sqlite3
from datetime import date
from starlette.concurrency import run_in_threadpool
from ...context_data import ContextBlock
from .domain import POLICY, encoded, instructions


async def select(store, scope, query=""):
    if scope is None:
        return None, None
    try:
        preferences, context = await asyncio.wait_for(run_in_threadpool(
            store.select, date.fromisoformat(scope.local_date), scope.conversation_id, query), timeout=.2)
    except (TimeoutError, sqlite3.Error, OSError):
        return None, {"status": "unavailable", "sources": [], "emotion_summary": None}
    return context, {
        "status": "ready" if any(preferences.values()) else "off",
        "sources": context["sources"], "emotion_summary": context["emotion_summary"],
        "chat_coverage": context["chat_coverage"],
    }


async def prepare(store, scope, query=""):
    # Voice retains its existing startup-only snapshot contract.
    context, report = await select(store, scope, query)
    return instructions(context), report


async def prepare_typed(store, scope, query=""):
    context, report = await select(store, scope, query)
    block = ContextBlock(POLICY, "PERSONAL_CONTEXT_JSON:\n" + encoded(context)) if context and context["sources"] else ContextBlock()
    return block, report
