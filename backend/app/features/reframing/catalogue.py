"""Compact voice startup definitions; no vectors, user text or personal storage."""
import asyncio
from ...context_data import ContextBlock
from .corpus import load_corpus
from .domain import InvalidKnowledge, REFERENCE_POLICY, canonical

# Leave headroom for rendered message framing under Live's 8,192-input-token cap.
# UTF-8 bytes are a conservative bound; do not discard user history to fit cards.
MAX_STARTUP_CONTENT_BYTES = 7500

CATALOGUE_POLICY = REFERENCE_POLICY + (
    ' This session may include a startup catalogue of all active conversational operations. '
    'It is reference data, not a user message asking for a response. Do not read it aloud. '
    'Use a relevant operation when invited; do not claim a vector lookup or ongoing search. '
    'Card sources are zero-based indices into the sources array. Cite only the supplied '
    'bibliographic details; no page or section locators are supplied in this compact catalogue. '
    'Definitions and boundaries are available at startup, not proof a reply used them.'
)


def catalogue_block(corpus, history_bytes=0):
    if type(history_bytes) is not int or not 0 <= history_bytes <= 6000:
        raise InvalidKnowledge('Invalid voice history budget.')
    sources = list(corpus.sources.values())
    positions = {source['id']: i for i, source in enumerate(sources)}
    cards = [{key: card[key] for key in ('id', 'operation', 'avoid')} | {
        'sources': sorted({positions[ref['source_id']] for ref in card['sources']})
    } for card in corpus.active]
    payload = {'corpus_revision': corpus.revision, 'corpus_sha256': corpus.fingerprint,
               'delivery': 'startup_catalogue', 'cards': cards,
               'sources': [{key: source[key] for key in ('id', 'title', 'authors', 'edition')} for source in sources]}
    data = 'REFRAMING_TECHNIQUE_REFERENCE\n' + canonical(payload)
    if len(data.encode('utf-8')) + history_bytes > MAX_STARTUP_CONTENT_BYTES:
        raise InvalidKnowledge('Voice startup reference budget exceeded.')
    return ContextBlock(CATALOGUE_POLICY, data), {'status': 'ready', 'card_ids': [c['id'] for c in cards], 'delivery': 'startup_catalogue'}


async def prepare_catalogue(history_bytes, *, enabled=False):
    if not enabled:
        return ContextBlock(), None
    try:
        return await asyncio.wait_for(asyncio.to_thread(lambda: catalogue_block(load_corpus(), history_bytes)), .2)
    except (TimeoutError, InvalidKnowledge, OSError, UnicodeError):
        return ContextBlock(), {'status': 'unavailable', 'card_ids': [], 'delivery': 'startup_catalogue'}
