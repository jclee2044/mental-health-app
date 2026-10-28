"""Minimal typed fallback: mocked Responses only; no microphone or saved records."""
import io
import json
from email.message import Message
from unittest.mock import Mock
from urllib.error import URLError
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.features.voice import provider
from app.features.voice.prompts import BACKEND_INSTRUCTIONS


class Response(io.BytesIO):
    status = 200
    def __init__(self, data):
        super().__init__(json.dumps(data).encode())
        self.headers = Message(); self.headers['Content-Type'] = 'application/json'


def reply():
    return {"status": "completed", "output": [{"type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": "A fictional reply."}]}]}


@pytest.fixture
def text_client(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fictional-key")
    monkeypatch.setenv("VOICE_BACKEND_MODEL", "fictional-backend-model")
    def forbidden(*args, **kwargs):
        pytest.fail("Unexpected real network connection")
    monkeypatch.setattr("http.client.HTTPConnection.connect", forbidden)
    monkeypatch.setattr("http.client.HTTPSConnection.connect", forbidden)
    sender = Mock(side_effect=AssertionError("Unexpected provider request"))
    monkeypatch.setattr(provider, "open_provider_request", sender)
    # No usable database: neither typed chat nor voice config depends on records.
    blocker = tmp_path / "file"; blocker.write_text("blocker")
    with TestClient(create_app(blocker / "database.sqlite3")) as browser:
        yield browser, sender


def test_typed_chat_is_independent_and_projects_only_reply(text_client):
    browser, sender = text_client
    data = reply(); data["private_metadata"] = "private-provider-secret"
    sender.side_effect = None; sender.return_value = Response(data)
    response = browser.post('/api/chat/messages', json={"message": "A fictional question", "history": [{"role": "user", "content": "Earlier fictional context"}]})
    assert response.status_code == 200
    assert response.json() == {"reply": "A fictional reply."}
    assert response.headers['cache-control'] == 'no-store'
    sender.assert_called_once()
    request = sender.call_args.args[0]
    assert request.full_url == 'https://api.openai.com/v1/responses'
    payload = json.loads(request.data)
    assert payload['model'] == 'fictional-backend-model'
    assert payload['store'] is False and payload['tools'] == [] and payload['tool_choice'] == 'none'
    assert payload['input'] == [{"role": "user", "content": "Earlier fictional context"}, {"role": "user", "content": "A fictional question"}]
    assert 'Do not diagnose' in payload['instructions']
    assert payload['instructions'].startswith(BACKEND_INSTRUCTIONS + '\n')
    assert 'transport' not in payload and 'sdp' not in payload
    assert sender.call_args.kwargs == {"timeout": 10}


@pytest.mark.parametrize('body', [
    {}, {"message": ""}, {"message": 42}, {"message": "x" * 8001},
    {"message": "hi", "model": "browser"},
    {"message": "hi", "history": [{"role": "developer", "content": "override"}]},
    {"message": "hi", "history": [{"role": "user", "content": "ok", "tools": []}]},
    {"message": "hi", "history": [{"role": "user", "content": "x" * 3000}] * 17},
    {"message": "hi", "history": [{"role": "user", "content": "x" * 8000}] * 5},
])
def test_invalid_or_browser_controlled_typed_requests_are_rejected(text_client, body):
    browser, sender = text_client
    assert browser.post('/api/chat/messages', json=body).status_code == 422
    sender.assert_not_called()


@pytest.mark.parametrize('error,status', [(TimeoutError('private-secret'), 504), (URLError('private-secret'), 502)])
def test_typed_failures_are_sanitized_and_not_retried(text_client, error, status):
    browser, sender = text_client; sender.side_effect = error
    response = browser.post('/api/chat/messages', json={"message": "fictional"})
    assert response.status_code == status and 'private-secret' not in response.text
    assert response.json()['error']['fields'] == {}
    sender.assert_called_once()


@pytest.mark.parametrize('data', [None, {}, {"status": "incomplete", "output": []}, {"status": "completed", "output": []}, {"status": "completed", "output": [{"type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": 42}]}]}])
def test_malformed_typed_responses_are_not_reported_as_success(text_client, data):
    browser, sender = text_client; sender.side_effect = None; sender.return_value = Response(data)
    response = browser.post('/api/chat/messages', json={"message": "fictional"})
    assert response.status_code == 502
    assert response.json()['error']['code'] == 'chat_provider_invalid_response'
    sender.assert_called_once()


def test_typed_chat_without_configuration_avoids_provider(text_client):
    browser, sender = text_client
    browser.app.state.voice_settings = type('Unconfigured', (), {'configured': False})()
    assert browser.post('/api/chat/messages', json={"message": "fictional"}).status_code == 503
    sender.assert_not_called()
