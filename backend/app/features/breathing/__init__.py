"""Feature registration; no imports from sibling features."""
from .routes import router
from .storage import BreathingStorage


def register(app, database):
    store = BreathingStorage(database)
    app.state.breathing_store = store
    app.include_router(router)
    return store
