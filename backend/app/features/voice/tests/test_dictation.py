"""Fictional audio containers and mocked provider; no network/audio devices."""
import base64
import io
import json
from email.message import Message
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.features.voice import provider
from app.features.voice.dictation_domain import MAX_DICTATION_BODY

AUDIO = b'\x1a\x45\xdf\xa3fictional-audio'
BODY = {'audio': base64.b64encode(AUDIO).decode(), 'mime_type': 'audio/webm'}

class Response(io.BytesIO):
    status = 200
    def __init__(self, data):
        super().__init__(json.dumps(data).encode())
        self.headers = Message(); self.headers['Content-Type'] = 'application/json'

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'fictional-key')
    monkeypatch.delenv('VOICE_BACKEND_MODEL', raising=False)
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected real network')
    monkeypatch.setattr('http.client.HTTPConnection.connect', forbidden)
    monkeypatch.setattr('http.client.HTTPSConnection.connect', forbidden)
    sender = Mock(return_value=Response({'text': ' A small win. ', 'ignored': 'private'}))
    monkeypatch.setattr(provider, 'open_provider_request', sender)
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as browser:
        yield browser, sender

def test_transcription_projects_text_and_uses_only_fixed_server_policy(client):
    browser, sender = client
    response = browser.post('/api/chat/transcriptions', json=BODY)
    assert response.status_code == 200 and response.json() == {'text': 'A small win.'}
    assert response.headers['cache-control'] == 'no-store'
    sender.assert_called_once()
    request = sender.call_args.args[0]
    assert request.full_url == 'https://api.openai.com/v1/audio/transcriptions'
    assert b'gpt-transcribe' in request.data and b'dictation.webm' in request.data and AUDIO in request.data
    assert b'name="model"' in request.data and b'name="response_format"' in request.data
    assert b'tools' not in request.data and b'instructions' not in request.data
    assert sender.call_args.kwargs == {'timeout': 20}

@pytest.mark.parametrize('body', [{}, {**BODY, 'model': 'override'}, {**BODY, 'audio': '!'}, {**BODY, 'audio': ''}, {**BODY, 'mime_type': 'text/plain'}, {**BODY, 'mime_type': []}, {**BODY, 'audio': base64.b64encode(b'wrong prefix').decode()}])
def test_invalid_audio_never_contacts_provider(client, body):
    browser, sender = client
    assert browser.post('/api/chat/transcriptions', json=body).status_code == 422
    sender.assert_not_called()

def test_wire_query_duplicate_and_media_bounds(client):
    browser, sender = client
    assert browser.post('/api/chat/transcriptions?model=x', json=BODY).status_code == 422
    assert browser.post('/api/chat/transcriptions', content='{}').status_code == 415
    assert browser.post('/api/chat/transcriptions', content='{"audio":"x","audio":"y"}', headers={'Content-Type': 'application/json'}).status_code == 422
    assert browser.post('/api/chat/transcriptions', content=b'x' * (MAX_DICTATION_BODY + 1), headers={'Content-Type': 'application/json'}).status_code == 413
    sender.assert_not_called()

@pytest.mark.parametrize('data', [{}, {'text': ''}, {'text': 42}, {'text': 'x' * 4001}, {'text': '界' * 3000}])
def test_invalid_transcripts_fail_closed(client, data):
    browser, sender = client; sender.return_value = Response(data)
    response = browser.post('/api/chat/transcriptions', json=BODY)
    assert response.status_code == 502 and response.json()['error']['code'] == 'dictation_invalid_response'

@pytest.mark.parametrize('error,status', [(TimeoutError('private'), 504), (OSError('private'), 502)])
def test_failures_sanitized_no_retry(client, error, status):
    browser, sender = client; sender.side_effect = error
    response = browser.post('/api/chat/transcriptions', json=BODY)
    assert response.status_code == status and 'private' not in response.text
    sender.assert_called_once()

def test_missing_key(client):
    browser, sender = client
    browser.app.state.voice_settings = type('Missing', (), {'api_key': ''})()
    assert browser.post('/api/chat/transcriptions', json=BODY).status_code == 503
    sender.assert_not_called()

def test_decoded_size_and_streamed_wire_limits(client):
    browser, sender = client
    too_big = base64.b64encode(b'\x1a\x45\xdf\xa3' + b'x' * (2 * 1024 * 1024)).decode()
    assert browser.post('/api/chat/transcriptions', json={**BODY, 'audio': too_big}).status_code == 422
    assert browser.post('/api/chat/transcriptions', content=iter([b'x' * MAX_DICTATION_BODY, b'x']), headers={'Content-Type': 'application/json'}).status_code == 413
    sender.assert_not_called()

def test_mp4_is_forwarded_with_server_owned_filename(client):
    browser, sender = client
    audio = b'\x00\x00\x00\x18ftypisomfictional'
    assert browser.post('/api/chat/transcriptions', json={'audio': base64.b64encode(audio).decode(), 'mime_type': 'audio/mp4'}).status_code == 200
    assert b'dictation.mp4' in sender.call_args.args[0].data
