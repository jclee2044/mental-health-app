"""Feature registration; no imports from sibling features."""
from .routes import router
from .storage import EmotionStorage


def register(app, database):
    store = EmotionStorage(database)
    app.state.emotion_store = store
    app.include_router(router)
    return store
