"""Personal history is separate from curated technique/reframing retrieval."""
from .routes import router
from .storage import MemoryStorage
from .summary_routes import summary_router


def register(app, database):
    app.state.personal_memory = MemoryStorage(database)
    app.include_router(router)
    app.include_router(summary_router)
    return app.state.personal_memory
