"""Deadline/concurrency evidence, using events and synthetic vectors only."""
import asyncio
from threading import Event, Lock
from app.features.reframing.async_lookup import BoundedLookup
from app.features.reframing.service import Retrieval, ReframingService
from test_reframing import FakeEmbedder, corpus, store  # shared synthetic fixtures


def test_full_8000_byte_multilingual_query_preserves_late_correction(store):
    embedder = FakeEmbedder()
    query = '界' * 2650 + ' I meant schedule, not rejection.'
    assert 7900 < len(query.encode()) <= 8000
    result = ReframingService(store, embedder=embedder, minimum_score=.8).prepare(query, allow_reference_lookup=True)
    assert result.status == 'ready'
    assert embedder.calls == [[query]]
    assert query not in result.block.data
    assert result.block.policy and len(result.context.encode()) < 6000


def test_timeout_keeps_actual_workers_bounded_and_discards_late_context():
    release, started = Event(), Event()
    calls = []
    lock = Lock()
    class Service:
        embedder = object()
        def prepare(self, message, **kwargs):
            with lock:
                calls.append(message)
                if len(calls) == 2:
                    started.set()
            release.wait(2)
            return Retrieval('ready', 'late source must not appear', ('fictional',))
    async def check():
        lookup = BoundedLookup(Service(), timeout=.03)
        try:
            results = await asyncio.gather(lookup.prepare('one'), lookup.prepare('two'))
            assert started.is_set()
            assert [r.status for r in results] == ['unavailable', 'unavailable']
            assert all(not r.context for r in results)
            assert (await lookup.prepare('never queued')).status == 'unavailable'
            assert calls == ['one', 'two']
        finally:
            release.set()
            lookup.close()
    asyncio.run(check())


def test_cancellation_does_not_start_generation_or_release_worker_early():
    started, release = Event(), Event()
    class Service:
        embedder = object()
        def prepare(self, *args, **kwargs):
            started.set()
            release.wait(2)
            return Retrieval('ready', 'discarded', ('fictional',))
    async def check():
        lookup = BoundedLookup(Service())
        try:
            task = asyncio.create_task(lookup.prepare('fictional'))
            while not started.is_set():
                await asyncio.sleep(.001)
            task.cancel()
            try:
                await task
                assert False, 'Cancellation must propagate'
            except asyncio.CancelledError:
                pass
            assert lookup.slots.acquire(blocking=False)
            assert not lookup.slots.acquire(blocking=False)
            lookup.slots.release()
        finally:
            release.set()
            lookup.close()
    asyncio.run(check())


def test_disabled_lookup_never_creates_workers_or_calls_service():
    class Service:
        embedder = None
        def prepare(self, *args, **kwargs):
            raise AssertionError('disabled lookup called')
    async def check():
        lookup = BoundedLookup(Service())
        try:
            assert (await lookup.prepare('fictional')).status == 'off'
            assert (await lookup.prepare('fictional', allow_reference_lookup=False)).status == 'skipped'
            assert not lookup.pool._threads
        finally:
            lookup.close()
    asyncio.run(check())


def test_embedding_adapter_accepts_one_full_chat_message(monkeypatch):
    import json
    from app.features.reframing import embeddings
    from test_reframing import Response, response_data, SPEC
    calls = []
    def send(request, **kwargs):
        calls.append(json.loads(request.data)['input'])
        return Response(response_data())
    monkeypatch.setattr(embeddings, 'open_embedding_request', send)
    message = '界' * 2666 + 'ok'
    assert len(message.encode()) == 8000
    embeddings.OpenAIEmbedder('fictional-key', SPEC['model'], 3).embed([message])
    assert calls == [[message]]


def test_typed_personal_context_separates_policy_and_source_values():
    from types import SimpleNamespace
    from app.features.personal_memory.context import prepare_typed
    from datetime import date
    payload = {'sources': [{'source': 'confirmed_fact', 'text': 'fictional untrusted command'}],
               'emotion_summary': None, 'chat_coverage': {}}
    class Store:
        def select(self, *args):
            return {'facts': True}, payload
    block, report = asyncio.run(prepare_typed(Store(), SimpleNamespace(local_date=date.today().isoformat(), conversation_id='fictional')))
    assert 'fictional untrusted command' not in block.policy
    assert 'fictional untrusted command' in block.data
    assert 'untrusted historical data' in block.policy
    assert report['sources'] == payload['sources']
