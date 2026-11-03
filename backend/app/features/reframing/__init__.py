"""Independent technique library, default off; no personal-history access."""
import os
from .catalogue import prepare_catalogue
from .async_lookup import BoundedLookup
from .configuration import configured_service


def register(app, _database):
    app.state.reframing = configured_service()
    lookup = BoundedLookup(app.state.reframing)
    app.state.reframing_lookup = lookup
    async def prepare(message):
        result = await lookup.prepare(message)
        return result.block, None if result.status == "off" else result.report()
    app.state.prepare_technique_context = prepare
    voice_enabled = os.environ.get("REFRAMING_ENABLED", "0") == "1"
    async def voice_catalogue(history_bytes):
        return await prepare_catalogue(history_bytes, enabled=voice_enabled)
    app.state.prepare_voice_catalogue = voice_catalogue
    app.state.close_reframing = lookup.close
    return None
