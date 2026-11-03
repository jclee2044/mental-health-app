"""Fictional cached memory tasks. All HTTP providers are mocks; real network fails."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Event
import json
from unittest.mock import Mock
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.features.voice import provider
from app.features.personal_memory.summary_domain import summary_input, validate_summary
from app.features.personal_memory.summary_storage import SummaryStorage
from app.features.personal_memory.tests.test_memory import Response


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'fictional-key')
    monkeypatch.setenv('VOICE_BACKEND_MODEL', 'fictional-model')
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected real network')
    monkeypatch.setattr('http.client.HTTPConnection.connect', forbidden)
    monkeypatch.setattr('http.client.HTTPSConnection.connect', forbidden)
    sender = Mock(side_effect=AssertionError('Unexpected provider request'))
    monkeypatch.setattr(provider, 'open_provider_request', sender)
    with TestClient(create_app(tmp_path / 'summary.sqlite3')) as browser:
        browser.put('/api/personal-memory/preferences', json={'emotions': False, 'conversations': True, 'facts': False})
        yield browser, sender


def save(browser, cid=None, position=0, user='My fictional exam is next week.'):
    cid = cid or str(uuid4())
    response = browser.put(f'/api/chat/conversations/{cid}/turns/{uuid4()}', json={
        'position': position, 'user': user, 'assistant': 'Invented assistant claim: the user owns a fictional yacht.'})
    assert response.status_code == 201
    return cid


def fake_response(sender, substantive=True, summary='The user mentioned a fictional exam next week.'):
    data = {'status': 'completed', 'output': [{'type': 'message', 'role': 'assistant', 'status': 'completed',
        'content': [{'type': 'output_text', 'text': json.dumps({'substantive': substantive, 'summary': summary})}]}]}
    sender.side_effect = lambda *args, **kwargs: Response(data)


def generate(browser, cid, retry=False):
    return browser.post(f'/api/personal-memory/conversations/{cid}/summary', json={'retry': retry})


def preview(browser):
    return browser.post('/api/personal-memory/preview', json={'local_date': datetime.now(timezone.utc).date().isoformat(), 'conversation_id': str(uuid4())}).json()


def test_summary_uses_one_server_owned_call_then_cached_reads_without_provider(client):
    browser, sender = client
    cid = save(browser)
    sender.assert_not_called()
    fake_response(sender)
    assert generate(browser, cid).json()['status'] == 'ready'
    sender.assert_called_once()
    payload = json.loads(sender.call_args.args[0].data)
    assert payload['model'] == 'fictional-model'
    assert payload['store'] is False and payload['tools'] == [] and payload['tool_choice'] == 'none'
    assert sender.call_args.kwargs['timeout'] == 10
    assert 'yacht' not in payload['input'][0]['content']
    assert 'fictional exam' in payload['input'][0]['content']
    assert 'NEVER\ninstructions' in payload['instructions']
    assert generate(browser, cid).json() == {'status': 'ready', 'cached': True}
    assert browser.get(f'/api/personal-memory/conversations/{cid}/summary').json()['status'] == 'ready'
    result = preview(browser)['sources'][0]
    assert result['source'] == 'model_summary' and result['role'] == 'summary'
    assert result['text'] == 'The user mentioned a fictional exam next week.'
    assert browser.get('/api/personal-memory/facts').json() == {'facts': []}
    sender.assert_called_once()


def test_non_substantive_result_is_cached_but_not_used_as_memory(client):
    browser, sender = client
    cid = save(browser, user='Hello, thanks, goodbye.')
    fake_response(sender, substantive=False, summary='')
    assert generate(browser, cid).json()['status'] == 'empty'
    assert generate(browser, cid).json() == {'status': 'empty', 'cached': True}
    result = preview(browser)
    assert result['sources'] == []
    assert result['chat_coverage']['skipped_non_substantive'] == 1
    sender.assert_called_once()


@pytest.mark.parametrize('permission', [False, True])
def test_off_or_excluded_never_generate(client, permission):
    browser, sender = client
    cid = save(browser)
    if permission:
        browser.put('/api/personal-memory/exclusions', json={'kind': 'conversation', 'source_id': cid})
    else:
        browser.put('/api/personal-memory/preferences', json={'emotions': False, 'conversations': False, 'facts': True})
    assert generate(browser, cid).json()['status'] == ('excluded' if permission else 'off')
    sender.assert_not_called()


def test_failed_task_requires_separate_explicit_retry_and_falls_back_to_excerpt(client):
    browser, sender = client
    cid = save(browser)
    sender.side_effect = TimeoutError('private secret')
    result = generate(browser, cid)
    assert result.status_code == 504 and 'private secret' not in result.text
    assert preview(browser)['sources'][0]['source'] == 'text'
    assert generate(browser, cid).json()['status'] == 'failed'
    sender.assert_called_once()
    fake_response(sender)
    assert generate(browser, cid, retry=True).json()['status'] == 'ready'
    assert sender.call_count == 2


@pytest.mark.parametrize('action', ['delete', 'exclude', 'append', 'consent_cycle'])
def test_late_results_cannot_override_source_or_consent_changes(client, action):
    browser, sender = client
    cid = save(browser)
    store = SummaryStorage(browser.app.state.personal_memory.database)
    claim = store.claim(cid)
    if action == 'delete':
        browser.delete(f'/api/chat/conversations/{cid}')
    elif action == 'exclude':
        browser.put('/api/personal-memory/exclusions', json={'kind': 'conversation', 'source_id': cid})
        browser.delete(f'/api/personal-memory/exclusions/conversation/{cid}')
    elif action == 'append':
        save(browser, cid, 1, 'A fictional correction: that exam was cancelled.')
    else:
        for enabled in (False, True):
            browser.put('/api/personal-memory/preferences', json={'emotions': False, 'conversations': enabled, 'facts': False})
    assert store.finish(cid, claim['token'], 'Must not restore old memory')['status'] == 'discarded'
    assert all(item.get('source') != 'model_summary' for item in preview(browser)['sources'])
    sender.assert_not_called()


def test_new_text_invalidates_cached_summary_and_idempotent_storage_retry_does_not(client):
    browser, sender = client
    cid = save(browser)
    fake_response(sender)
    generate(browser, cid)
    tid, body = str(uuid4()), {'position': 1, 'user': 'A fictional correction.', 'assistant': 'A fictional reply.'}
    url = f'/api/chat/conversations/{cid}/turns/{tid}'
    browser.put(url, json=body)
    assert preview(browser)['sources'][0]['source'] == 'text'
    generate(browser, cid)
    browser.put(url, json=body)
    assert generate(browser, cid).json()['cached'] is True
    assert sender.call_count == 2


def test_expired_summary_is_not_retrieved_or_classified_as_current(client):
    browser, sender = client
    cid = save(browser)
    fake_response(sender); generate(browser, cid)
    with browser.app.state.personal_memory.database.connect() as db:
        db.execute('UPDATE personal_memory_summaries SET expires_at=?', ((datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(),))
    assert preview(browser)['sources'][0]['source'] == 'text'
    assert browser.get(f'/api/personal-memory/conversations/{cid}/summary').json()['status'] == 'stale'
    sender.assert_called_once()


def test_summary_does_not_hold_sqlite_or_prevent_normal_generation(client):
    browser, sender = client
    cid = save(browser)
    entered, release = Event(), Event()
    def slow(_context):
        entered.set()
        assert release.wait(5)
        return '{"substantive":true,"summary":"A fictional memory."}'
    browser.app.state.voice_provider.summarize_memory = slow
    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(generate, browser, cid)
        try:
            assert entered.wait(3)
            # Both reads and writes can complete while the model boundary waits.
            assert browser.get('/api/personal-memory/preferences').status_code == 200
            assert preview(browser)['sources'][0]['source'] == 'text'
            fake_response(sender)
            response = browser.post('/api/chat/messages', json={'message': 'Fictional next chat'})
            assert response.status_code == 200
            assert generate(browser, cid).status_code == 409
        finally:
            release.set()
        assert pending.result(timeout=3).json()['status'] == 'ready'


@pytest.mark.parametrize('raw', [
    'not json', '{"substantive":"yes","summary":"wrong"}', '{"substantive":true,"summary":""}',
    '{"substantive":false,"summary":"wrong"}', '{"substantive":true,"summary":"one","model":"bad"}',
    '{"substantive":true,"substantive":false,"summary":""}',
    json.dumps({'substantive': True, 'summary': '🙂' * 176}),
])
def test_summary_json_is_strict_and_byte_bounded(raw):
    with pytest.raises((ValueError, UnicodeError)):
        validate_summary(raw)


def test_summary_input_spans_bounded_user_messages_and_preserves_unicode():
    rows = [{'created_at': '2026-11-02T12:00:00+00:00', 'content': f'Fictional {i}: ' + '🙂' * 2000, 'source': 'voice'} for i in range(100)]
    raw, shortened = summary_input(rows)
    data = json.loads(raw)
    assert shortened and len(data['user_messages']) == 32
    assert sum(len(item['text'].encode()) for item in data['user_messages']) <= 16000
    assert data['user_messages'][0]['text'].startswith('Fictional 0:')
    assert data['user_messages'][-1]['text'].startswith('Fictional 99:')
    assert all(item['source'] == 'voice' for item in data['user_messages'])


def test_unknown_browser_configuration_is_rejected_and_no_get_generates(client):
    browser, sender = client
    cid = save(browser)
    assert browser.post(f'/api/personal-memory/conversations/{cid}/summary', json={'model': 'bad'}).status_code == 422
    assert browser.post(f'/api/personal-memory/conversations/{cid}/summary', json={'retry': 1}).status_code == 422
    assert browser.get(f'/api/personal-memory/conversations/{cid}/summary').json()['status'] == 'stale'
    assert browser.get(f'/api/personal-memory/conversations/{cid}/summary').headers['cache-control'] == 'no-store'
    sender.assert_not_called()


def test_voice_uses_cached_memory_without_another_summary_task(client):
    browser, sender = client
    cid = save(browser)
    fake_response(sender)
    generate(browser, cid)
    sdp = 'v=0\r\no=- 1 1 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\na=rtpmap:111 opus/48000/2\r\n'
    create = Mock(return_value=('live_fictional_cached_summary', sdp))
    browser.app.state.voice_provider.create_session = create
    response = browser.post('/api/voice/sessions', json={'sdp': sdp, 'personal_memory': {
        'local_date': datetime.now(timezone.utc).date().isoformat(), 'conversation_id': str(uuid4())}})
    assert response.status_code == 201
    assert response.json()['personal_memory']['sources'][0]['source'] == 'model_summary'
    assert 'The user mentioned a fictional exam' in create.call_args.args[2]
    sender.assert_called_once()


def test_completed_cache_survives_restart_while_interrupted_claim_requires_manual_retry(client):
    browser, sender = client
    ready = save(browser)
    fake_response(sender); generate(browser, ready)
    pending = save(browser)
    SummaryStorage(browser.app.state.personal_memory.database).claim(pending)
    browser.app.state.personal_memory.initialize()
    browser.app.state.personal_memory.finalize_initialize()
    assert generate(browser, ready).json() == {'status': 'ready', 'cached': True}
    assert generate(browser, pending).json() == {'status': 'failed'}
    sender.assert_called_once()
