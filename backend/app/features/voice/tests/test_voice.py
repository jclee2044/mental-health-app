"""Fictional SDP and mocked HTTP only; real network access is forbidden."""
import io
import json
from email.message import Message
from http.client import HTTPException
from unittest.mock import Mock
from urllib.error import HTTPError, URLError
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.features.voice import provider
from app.features.voice.domain import MAX_BODY_BYTES, MAX_PROVIDER_BYTES, MAX_SDP_BYTES
from app.features.voice.prompts import BACKEND_INSTRUCTIONS, LIVE_INSTRUCTIONS
from app.features.voice.settings import SERVER_EVENTS, VOICE_DURATION_SECONDS, VoiceSettings, session_payload

KEY = "fictional-key-for-mocked-tests"
BACKEND_MODEL = "fictional-responses-model"
SDP = "v=0\r\no=- 1 1 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\na=rtpmap:111 opus/48000/2\r\n"
ANSWER = SDP + "a=setup:active\r\n"


def valid_response():
    return {"session": {"id": "live_fictional_123"}, "transport": {"type": "webrtc", "sdp": ANSWER}}


class FakeResponse:
    def __init__(self, data=None, *, raw=None, status=201, content_type="application/json"):
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        self.stream = io.BytesIO(raw if raw is not None else json.dumps(data).encode())
        self.closed = False
        self.read_limits = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True
        self.stream.close()

    def read(self, size):
        self.read_limits.append(size)
        return self.stream.read(size)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("A test attempted a real provider connection")
    monkeypatch.setattr("http.client.HTTPConnection.connect", forbidden)
    monkeypatch.setattr("http.client.HTTPSConnection.connect", forbidden)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", KEY)
    monkeypatch.setenv("VOICE_BACKEND_MODEL", BACKEND_MODEL)
    sender = Mock(side_effect=AssertionError("Unexpected provider request"))
    monkeypatch.setattr(provider, "open_provider_request", sender)
    with TestClient(create_app(tmp_path / "test.sqlite3")) as browser:
        yield browser, sender


@pytest.mark.parametrize("key", [None, "", "  ", "bad\r\nheader", "x" * 4097, KEY])
def test_configuration_and_missing_credentials(tmp_path, monkeypatch, key):
    monkeypatch.setenv("VOICE_BACKEND_MODEL", BACKEND_MODEL)
    if key is None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    else:
        monkeypatch.setenv("OPENAI_API_KEY", key)
    sender = Mock(side_effect=AssertionError("No provider request expected"))
    monkeypatch.setattr(provider, "open_provider_request", sender)
    with TestClient(create_app(tmp_path / "test.sqlite3")) as browser:
        response = browser.get("/api/voice/config")
        assert response.status_code == 200
        assert response.json() == {"status": "configured" if key == KEY else "unconfigured", "duration_seconds": VOICE_DURATION_SECONDS}
        assert response.headers["cache-control"] == "no-store"
        if key != KEY:
            result = browser.post("/api/voice/sessions", json={"sdp": SDP})
            assert result.status_code == 503
            assert result.json()["error"]["code"] == "voice_unconfigured"
        sender.assert_not_called()
    assert KEY not in repr(VoiceSettings(api_key=KEY))


def test_success_projects_response_and_keeps_policy_server_owned(client):
    browser, sender = client
    data = valid_response()
    data["session"].update(api_key=KEY, instructions=LIVE_INSTRUCTIONS)
    data["client_secret"] = KEY
    response = FakeResponse(data)
    sender.side_effect = None
    sender.return_value = response
    result = browser.post("/api/voice/sessions", json={"sdp": SDP})
    assert result.status_code == 201
    assert result.json() == {"session_id": "live_fictional_123", "sdp": ANSWER, "duration_seconds": VOICE_DURATION_SECONDS}
    assert result.headers["cache-control"] == "no-store"
    sender.assert_called_once()
    request = sender.call_args.args[0]
    assert request.full_url == "https://api.openai.com/v1/live/sessions"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == f"Bearer {KEY}"
    assert sender.call_args.kwargs == {"timeout": 10}
    payload = json.loads(request.data)
    assert payload["transport"] == {"type": "webrtc", "sdp": SDP}
    session = payload["session"]
    assert session["model"] == "gpt-live-1" and session["instructions"] == LIVE_INSTRUCTIONS
    assert session["store"] is False
    assert session["delegation"] == {"type": "responses", "responses": {
        "model": BACKEND_MODEL, "instructions": BACKEND_INSTRUCTIONS,
        "tools": [], "tool_choice": "none",
    }}
    assert LIVE_INSTRUCTIONS != BACKEND_INSTRUCTIONS
    assert session["triggers"] == []
    assert "tools" not in session and "responses" not in session
    permissions = session["client"]["data_channel"]
    assert permissions["allowed_client_events"] == ["session.close"]
    assert session["input"] == []
    assert permissions["allowed_server_events"] == [{"type": event} for event in SERVER_EVENTS]
    assert response.closed and response.read_limits == [MAX_PROVIDER_BYTES + 1]


@pytest.mark.parametrize("field", ["model", "api_key", "instructions", "prompt", "provider_url", "tools", "policy", "duration_seconds", "store", "session", "transport", "profile_id", "owner_id", "allowed_client_events", "backend_model", "VOICE_BACKEND_MODEL", "backend_instructions", "delegation", "audio", "transcript", "input", "session_id"])
def test_browser_configuration_and_unneeded_identity_are_rejected(client, field):
    browser, sender = client
    response = browser.post("/api/voice/sessions", json={"sdp": SDP, field: KEY})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["fields"] == {}
    assert KEY not in response.text
    sender.assert_not_called()


@pytest.mark.parametrize("body", [{}, {"sdp": None}, {"sdp": 42}, {"sdp": {}}, [], {"sdp": True}])
def test_invalid_json_shapes_do_not_call_provider(client, body):
    browser, sender = client
    assert browser.post("/api/voice/sessions", json=body).status_code == 422
    sender.assert_not_called()


@pytest.mark.parametrize("sdp", ["", "hello", "v=0\r\n", SDP.replace("v=0", "v=1"), SDP.replace("m=audio", "m=video"), SDP + "\x00", SDP + "broken-line\r\n", SDP + "a=bad\rline\n", SDP + "a=bad\ud800\n"])
def test_invalid_sdp_does_not_call_provider(client, sdp):
    browser, sender = client
    result = browser.post("/api/voice/sessions", content=json.dumps({"sdp": sdp}), headers={"Content-Type": "application/json"})
    assert result.status_code == 422
    assert result.json()["error"]["code"] == "invalid_sdp"
    sender.assert_not_called()


def test_sdp_byte_bound_and_exact_boundary(client):
    browser, sender = client
    exact = SDP + "a=" + "x" * (MAX_SDP_BYTES - len(SDP.encode()) - 4) + "\r\n"
    assert len(exact.encode()) == MAX_SDP_BYTES
    sender.side_effect = None
    sender.return_value = FakeResponse(valid_response())
    assert browser.post("/api/voice/sessions", json={"sdp": exact}).status_code == 201
    sender.reset_mock()
    for oversized in [exact + "x", SDP + "a=" + "é" * (MAX_SDP_BYTES // 2)]:
        result = browser.post("/api/voice/sessions", content=json.dumps({"sdp": oversized}, ensure_ascii=False).encode(), headers={"Content-Type": "application/json"})
        assert result.status_code == 413
        assert result.json()["error"]["code"] == "sdp_too_large"
    sender.assert_not_called()


@pytest.mark.parametrize("streamed", [False, True])
def test_wire_body_bound_before_parsing(client, streamed):
    browser, sender = client
    raw = b" " * (MAX_BODY_BYTES + 1)
    result = browser.post("/api/voice/sessions", content=iter([raw]) if streamed else raw, headers={"Content-Type": "application/json"})
    assert result.status_code == 413
    assert result.json()["error"]["code"] == "request_too_large"
    sender.assert_not_called()


@pytest.mark.parametrize("raw", [b"{", b"{\"sdp\":NaN}", b"{\"sdp\":\"first\",\"sdp\":\"second\"}", b"[" * 1200 + b"]" * 1200])
def test_malformed_json_is_sanitized(client, raw):
    browser, sender = client
    result = browser.post("/api/voice/sessions", content=raw, headers={"Content-Type": "application/json"})
    assert result.status_code == 422
    assert result.json()["error"]["fields"] == {}
    sender.assert_not_called()


def test_query_configuration_and_non_json_rejected(client):
    browser, sender = client
    assert browser.get("/api/voice/config?api_key=secret").status_code == 422
    assert browser.post("/api/voice/sessions?model=override", json={"sdp": SDP}).status_code == 422
    assert browser.post("/api/voice/sessions", content=SDP, headers={"Content-Type": "application/sdp"}).status_code == 415
    sender.assert_not_called()


@pytest.mark.parametrize("error,status,code", [
    (URLError("provider-secret"), 502, "voice_provider_unavailable"),
    (OSError("provider-secret"), 502, "voice_provider_unavailable"),
    (HTTPException("provider-secret"), 502, "voice_provider_unavailable"),
    (TimeoutError("provider-secret"), 504, "voice_provider_timeout"),
    (URLError(TimeoutError("provider-secret")), 504, "voice_provider_timeout"),
])
def test_provider_failures_are_sanitized_without_retry(client, error, status, code):
    browser, sender = client
    sender.side_effect = error
    response = browser.post("/api/voice/sessions", json={"sdp": SDP})
    assert response.status_code == status
    assert response.json()["error"] == {"code": code, "message": response.json()["error"]["message"], "fields": {}}
    assert "provider-secret" not in response.text and KEY not in response.text
    assert response.headers["cache-control"] == "no-store"
    sender.assert_called_once()


@pytest.mark.parametrize("status", [301, 302, 307, 401, 429, 500])
def test_provider_http_errors_close_body_without_leaking_or_retrying(client, status):
    browser, sender = client
    body = io.BytesIO(b"provider-secret")
    sender.side_effect = HTTPError(provider.PROVIDER_URL, status, "provider-secret", {}, body)
    result = browser.post("/api/voice/sessions", json={"sdp": SDP})
    assert result.status_code == 502
    assert "provider-secret" not in result.text and KEY not in result.text
    assert body.closed
    sender.assert_called_once()


@pytest.mark.parametrize("data", [
    None, [], {}, {"session": []},
    {"session": {"id": "live_ok"}, "transport": []},
    {"session": {"id": "live_ok"}, "transport": {"type": "sip", "sdp": ANSWER}},
    {"session": {"id": 123}, "transport": {"type": "webrtc", "sdp": ANSWER}},
    {"session": {"id": "bad\r\nsecret"}, "transport": {"type": "webrtc", "sdp": ANSWER}},
    {"session": {"id": "x" * 129}, "transport": {"type": "webrtc", "sdp": ANSWER}},
    {"session": {"id": "live_ok"}, "transport": {"type": "webrtc", "sdp": "provider-secret"}},
    {"session": {"id": "live_ok"}, "transport": {"type": "webrtc", "sdp": "x" * (MAX_SDP_BYTES + 1)}},
])
def test_invalid_provider_shapes_are_not_returned(client, data):
    browser, sender = client
    sender.side_effect = None
    response = FakeResponse(data)
    sender.return_value = response
    result = browser.post("/api/voice/sessions", json={"sdp": SDP})
    assert result.status_code == 502
    assert result.json()["error"]["code"] == "voice_provider_invalid_response"
    assert "provider-secret" not in result.text
    assert response.closed
    sender.assert_called_once()


@pytest.mark.parametrize("raw,content_type", [(b"not-json-provider-secret", "application/json"), (b"\xff", "application/json"), (b"x" * (MAX_PROVIDER_BYTES + 1), "application/json"), (b"[" * 1200 + b"]" * 1200, "application/json"), (b"{}", "text/html")])
def test_provider_bytes_are_bounded_and_sanitized(client, raw, content_type):
    browser, sender = client
    sender.side_effect = None
    response = FakeResponse(raw=raw, content_type=content_type)
    sender.return_value = response
    result = browser.post("/api/voice/sessions", json={"sdp": SDP})
    assert result.status_code == 502
    assert result.json()["error"]["code"] == "voice_provider_invalid_response"
    assert "provider-secret" not in result.text and KEY not in result.text
    assert response.closed
    sender.assert_called_once()


def test_non_creation_status_is_rejected(client):
    browser, sender = client
    sender.side_effect = None
    sender.return_value = FakeResponse(valid_response(), status=200)
    assert browser.post("/api/voice/sessions", json={"sdp": SDP}).status_code == 502
    sender.assert_called_once()


def test_policy_is_fresh_and_redirects_are_not_followed(monkeypatch):
    payload = session_payload(SDP, BACKEND_MODEL)
    payload["session"]["client"]["data_channel"]["allowed_client_events"].append("session.update")
    payload["session"]["delegation"]["responses"]["tools"].append({"type": "web_search"})
    fresh = session_payload(SDP, BACKEND_MODEL)
    assert "session.update" not in fresh["session"]["client"]["data_channel"]["allowed_client_events"]
    assert fresh["session"]["delegation"]["responses"]["tools"] == []
    assert provider.NoRedirects().redirect_request(None, None, 307, "redirect", {}, "https://attacker.invalid") is None
    opener = Mock()
    builder = Mock(return_value=opener)
    monkeypatch.setattr(provider, "build_opener", builder)
    request = object()
    assert provider.open_provider_request(request, timeout=10) is opener.open.return_value
    assert isinstance(builder.call_args.args[0], provider.NoRedirects)
    opener.open.assert_called_once_with(request, timeout=10)


@pytest.mark.parametrize("model", [None, "", "  ", "bad\nmodel", "https://browser.invalid/model", "x" * 129, BACKEND_MODEL])
def test_backend_model_is_required_and_server_owned(tmp_path, monkeypatch, model):
    monkeypatch.setenv("OPENAI_API_KEY", KEY)
    if model is None:
        monkeypatch.delenv("VOICE_BACKEND_MODEL", raising=False)
    else:
        monkeypatch.setenv("VOICE_BACKEND_MODEL", model)
    sender = Mock(side_effect=AssertionError("Unexpected provider request"))
    monkeypatch.setattr(provider, "open_provider_request", sender)
    with TestClient(create_app(tmp_path / "test.sqlite3")) as browser:
        response = browser.get("/api/voice/config")
        assert response.json() == {"status": "configured" if model == BACKEND_MODEL else "unconfigured", "duration_seconds": VOICE_DURATION_SECONDS}
        assert KEY not in response.text and BACKEND_MODEL not in response.text
        if model != BACKEND_MODEL:
            assert browser.post("/api/voice/sessions", json={"sdp": SDP}).status_code == 503
        sender.assert_not_called()


def prepare_end(client):
    browser, sender = client
    sender.side_effect = [FakeResponse(valid_response()), FakeResponse(raw=b"", status=204)]
    assert browser.post("/api/voice/sessions", json={"sdp": SDP}).status_code == 201
    return browser, sender, "/api/voice/sessions/live_fictional_123/end"


def test_end_is_single_attempt_server_owned_and_idempotent(client):
    browser, sender, path = prepare_end(client)
    for _ in range(3):
        response = browser.post(path, json={})
        assert response.status_code == 204 and not response.content
        assert response.headers["cache-control"] == "no-store"
    assert sender.call_count == 2  # One creation, one hangup.
    request = sender.call_args.args[0]
    assert request.full_url == "https://api.openai.com/v1/live/sessions/live_fictional_123/hangup"
    assert request.get_method() == "POST" and json.loads(request.data) == {}
    assert request.get_header("Authorization") == f"Bearer {KEY}"
    assert sender.call_args.kwargs == {"timeout": 3}


@pytest.mark.parametrize("status,expected", [(200, 204), (204, 204), (201, 502), (500, 502)])
def test_end_accepts_only_empty_success_statuses(client, status, expected):
    browser, sender, path = prepare_end(client)
    sender.side_effect = None
    sender.return_value = FakeResponse(raw=b"", status=status)
    response = browser.post(path, json={})
    assert response.status_code == expected
    assert sender.call_count == 2


@pytest.mark.parametrize("body", [{"model": KEY}, {"session_id": "other"}, None, [], "", 0])
def test_end_rejects_configuration_and_nonempty_shapes(client, body):
    browser, sender = client
    result = browser.post("/api/voice/sessions/live_unknown/end", content=json.dumps(body), headers={"Content-Type": "application/json"})
    assert result.status_code == 422
    assert KEY not in result.text
    sender.assert_not_called()


def test_end_unknown_invalid_query_media_and_body_bounds(client):
    browser, sender = client
    path = "/api/voice/sessions/live_unknown/end"
    assert browser.post(path, json={}).status_code == 404
    assert browser.post(path + "?provider_url=override", json={}).status_code == 422
    assert browser.post(path, content="{}").status_code == 415
    assert browser.post(path, content=b"x" * (MAX_BODY_BYTES + 1), headers={"Content-Type": "application/json"}).status_code == 413
    for identifier in ["bad.id", "x" * 129, "é"]:
        assert browser.post(f"/api/voice/sessions/{identifier}/end", json={}).status_code == 422
    sender.assert_not_called()


@pytest.mark.parametrize("error,status", [(TimeoutError("provider-secret"), 504), (URLError("provider-secret"), 502)])
def test_end_failure_is_sanitized_without_retry_even_after_repeated_end(client, error, status):
    browser, sender, path = prepare_end(client)
    sender.side_effect = error
    response = browser.post(path, json={})
    assert response.status_code == status
    assert response.json()["error"]["code"] == "voice_close_unconfirmed"
    assert "provider-secret" not in response.text and KEY not in response.text
    assert browser.post(path, json={}).status_code == 502
    assert sender.call_count == 2


def test_concurrent_end_reports_closing_without_another_provider_attempt(client):
    browser, sender, path = prepare_end(client)
    assert browser.app.state.voice_provider.closures.begin("live_fictional_123") == "open"
    response = browser.post(path, json={})
    assert response.status_code == 202 and response.json() == {"status": "closing"}
    assert sender.call_count == 1


def test_disconnected_creation_closes_its_late_session(client, monkeypatch):
    from starlette.requests import Request
    async def disconnected(_request):
        return True
    monkeypatch.setattr(Request, "is_disconnected", disconnected)
    browser, sender = client
    sender.side_effect = [FakeResponse(valid_response()), FakeResponse(raw=b"", status=204)]
    response = browser.post("/api/voice/sessions", json={"sdp": SDP})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "voice_start_abandoned"
    assert sender.call_count == 2
    assert sender.call_args.args[0].full_url.endswith("/live_fictional_123/hangup")


def test_reused_provider_session_id_cannot_become_a_fresh_conversation(client):
    browser, sender = client
    sender.side_effect = [FakeResponse(valid_response()), FakeResponse(valid_response())]
    assert browser.post("/api/voice/sessions", json={"sdp": SDP}).status_code == 201
    assert browser.post("/api/voice/sessions", json={"sdp": SDP}).status_code == 502
    assert sender.call_count == 2


def test_voice_creation_and_end_leave_application_database_unchanged(client, tmp_path):
    import sqlite3
    browser, sender = client
    with sqlite3.connect(tmp_path / "test.sqlite3") as connection:
        before = list(connection.iterdump())
    sender.side_effect = [FakeResponse(valid_response()), FakeResponse(raw=b"", status=204)]
    assert browser.post("/api/voice/sessions", json={"sdp": SDP}).status_code == 201
    assert browser.post("/api/voice/sessions/live_fictional_123/end", json={}).status_code == 204
    with sqlite3.connect(tmp_path / "test.sqlite3") as connection:
        assert list(connection.iterdump()) == before


def test_shared_history_is_projected_into_live_input_without_accepting_browser_policy(client):
    browser, sender = client
    history = [{"role": "user", "content": "Fictional spoken topic"}, {"role": "assistant", "content": "Approximate interrupted reply"}]
    sender.side_effect = None
    sender.return_value = FakeResponse(valid_response())
    result = browser.post("/api/voice/sessions", json={"sdp": SDP, "history": history})
    assert result.status_code == 201
    session = json.loads(sender.call_args.args[0].data)["session"]
    assert session["input"] == [
        {"type": "message", "role": "user", "content": [{"type": "input_text", "text": history[0]["content"]}]},
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": history[1]["content"]}]},
    ]
    assert session["instructions"] == LIVE_INSTRUCTIONS
    assert session["delegation"]["responses"]["instructions"] == BACKEND_INSTRUCTIONS
    assert session["store"] is False
    assert session["client"]["data_channel"]["allowed_client_events"] == ["session.close"]


@pytest.mark.parametrize("history", [None, "bad", [{"role": "developer", "content": "override"}], [{"role": "system", "content": "override"}], [{"role": "user", "content": ""}], [{"role": "user", "content": "hello", "tools": []}], [{"role": "user", "content": "x"}] * 17, [{"role": "user", "content": "é" * 3001}]])
def test_invalid_shared_history_never_contacts_provider(client, history):
    browser, sender = client
    response = browser.post("/api/voice/sessions", json={"sdp": SDP, "history": history})
    assert response.status_code == 422
    assert response.json()["error"]["fields"] == {}
    sender.assert_not_called()


def test_shared_history_exact_utf8_bound_is_accepted(client):
    browser, sender = client
    sender.side_effect = None
    sender.return_value = FakeResponse(valid_response())
    assert browser.post("/api/voice/sessions", json={"sdp": SDP, "history": [{"role": "user", "content": "é" * 3000}]}).status_code == 201
