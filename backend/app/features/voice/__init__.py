"""Voice negotiation and typed chat, with independent typed-record storage."""
from .provider import LiveProvider
from .routes import router, text_router
from .settings import VoiceSettings
from .storage import ChatStorage
from .dictation_routes import dictation_router


def register(app, database):
    app.state.configure_chat_context = configure_context
    app.state.voice_settings = VoiceSettings.from_environment()
    app.state.voice_provider = LiveProvider(app.state.voice_settings)
    app.state.chat_store = ChatStorage(database)
    app.include_router(router)
    app.include_router(text_router)
    app.include_router(dictation_router)
    return app.state.chat_store


def configure_context(app):
    from ...conversation_context import ConversationContext, empty_context
    async def personal(message, scope):
        prepare = getattr(app.state, 'prepare_typed_memory', None)
        return await prepare(app.state.personal_memory, scope, message) if prepare else await empty_context()
    app.state.conversation_context = ConversationContext(personal, getattr(app.state, 'prepare_technique_context', empty_context))
