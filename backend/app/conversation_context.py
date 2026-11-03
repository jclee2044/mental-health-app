"""Compose independently owned sources; no sibling-feature imports."""
import asyncio
from .context_data import ContextBlock, TurnContext


class RequestAbandoned(Exception):
    pass


async def empty_context(*args):
    return ContextBlock(), None


class ConversationContext:
    def __init__(self, personal=empty_context, techniques=empty_context):
        self.personal = personal
        self.techniques = techniques

    async def prepare(self, message, scope, is_disconnected):
        if await is_disconnected():
            raise RequestAbandoned()
        personal, techniques = await asyncio.gather(self.personal(message, scope), self.techniques(message))
        if await is_disconnected():
            raise RequestAbandoned()
        return TurnContext(personal[0], techniques[0], personal[1], techniques[1])
