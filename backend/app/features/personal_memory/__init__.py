"""Personal history is separate from curated technique/reframing retrieval."""
from .routes import router
from .storage import MemoryStorage
from .summary_routes import summary_router


def register(app, database):
    from .context import prepare, prepare_typed
    from .summary_domain import SUMMARY_INSTRUCTIONS
    app.state.prepare_personal_memory = prepare
    app.state.prepare_typed_memory = prepare_typed
    app.state.memory_summary_instructions = SUMMARY_INSTRUCTIONS
    app.state.personal_memory = MemoryStorage(database)
    app.include_router(router)
    app.include_router(summary_router)
    return app.state.personal_memory
