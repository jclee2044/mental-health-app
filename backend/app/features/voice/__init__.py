"""Voice negotiation and typed chat, with independent typed-record storage."""
from .provider import LiveProvider
from .routes import router, text_router
from .settings import VoiceSettings
from .storage import ChatStorage
from .dictation_routes import dictation_router


def register(app, database):
    app.state.voice_settings = VoiceSettings.from_environment()
    app.state.voice_provider = LiveProvider(app.state.voice_settings)
    app.state.chat_store = ChatStorage(database)
    app.include_router(router)
    app.include_router(text_router)
    app.include_router(dictation_router)
    return app.state.chat_store
