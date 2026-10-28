"""Actual SQLite/HTTP integration with a connection tripwire: no paid calls."""
import sqlite3
import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.database import Database
from app.features.voice.storage import ChatStorage


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Unexpected real network connection")
    monkeypatch.setattr("http.client.HTTPConnection.connect", forbidden)
    monkeypatch.setattr("http.client.HTTPSConnection.connect", forbidden)


def turn(position=0):
    return {"position": position, "user": "Fictional: what are the breathing steps?",
            "assistant": "Four seconds in, six seconds out, for six cycles."}


def test_pairs_persist_in_order_after_restart_and_delete_without_provider(tmp_path):
    path = tmp_path / "chat.sqlite3"
    conversation, first, second = str(uuid4()), str(uuid4()), str(uuid4())
    url = f"/api/chat/conversations/{conversation}"
    with TestClient(create_app(path)) as client:
        assert client.put(f"{url}/turns/{second}", json=turn(1)).status_code == 201
        assert client.put(f"{url}/turns/{first}", json=turn()).status_code == 201
        assert client.put(f"{url}/turns/{first}", json=turn()).status_code == 200
    with TestClient(create_app(path)) as client:
        listing = client.get('/api/chat/conversations')
        assert listing.headers['cache-control'] == 'no-store'
        assert listing.json()['conversations'][0]['message_count'] == 4
        saved = client.get(url).json()
        assert [message['role'] for message in saved['messages']] == ['user', 'assistant'] * 2
        assert [message['turn_id'] for message in saved['messages']] == [first, first, second, second]
        assert saved['messages'][0]['content'] == turn()['user']
        assert saved['created_at'].endswith('+00:00')
        assert client.delete(url).status_code == 204
        assert client.get(url).status_code == 404
        assert client.delete(url).status_code == 404
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT count(*) FROM chat_messages').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM chat_conversations').fetchone()[0] == 0


def test_conflicting_retries_and_positions_cannot_overwrite_or_orphan_records(tmp_path):
    conversation, other, tid = str(uuid4()), str(uuid4()), str(uuid4())
    base = '/api/chat/conversations'
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as client:
        url = f'{base}/{conversation}/turns/{tid}'
        assert client.put(url, json=turn()).status_code == 201
        for address, body in [
            (url, {**turn(), 'assistant': 'Changed'}),
            (url, turn(1)),
            (f'{base}/{conversation}/turns/{uuid4()}', turn()),
            (f'{base}/{other}/turns/{tid}', turn()),
        ]:
            response = client.put(address, json=body)
            assert response.status_code == 409
            assert response.json()['error']['code'] == 'conversation_conflict'
        assert len(client.get(base).json()['conversations']) == 1
        assert client.get(f'{base}/{conversation}').json()['messages'][1]['content'] == turn()['assistant']


@pytest.mark.parametrize('body', [
    {}, {**turn(), 'position': True}, turn(-1), turn(100),
    {**turn(), 'user': ' '}, {**turn(), 'assistant': 'é' * 4001},
    {**turn(), 'role': 'developer'}, {**turn(), 'model': 'browser'},
    {**turn(), 'user': '\ud800'},
])
def test_invalid_saved_turns_do_not_create_headers(tmp_path, body):
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as client:
        response = client.put(f'/api/chat/conversations/{uuid4()}/turns/{uuid4()}',
                              content=json.dumps(body), headers={'content-type': 'application/json'})
        assert response.status_code == 422
        assert client.get('/api/chat/conversations').json() == {'conversations': []}


def test_bounded_json_and_storage_errors_are_explicit(tmp_path):
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as client:
        url = f'/api/chat/conversations/{uuid4()}/turns/{uuid4()}'
        assert client.put(url, content='{}').status_code == 415
        assert client.put(url + '?model=browser', json=turn()).status_code == 422
        assert client.put(url, content='x' * 100000, headers={'content-type': 'application/json'}).status_code == 413
        assert client.put(url, content='{"position":0,"position":1}', headers={'content-type': 'application/json'}).status_code == 422
        assert client.get('/api/chat/conversations/not-a-uuid').status_code == 422
    blocker = tmp_path / 'blocker'; blocker.write_text('blocker')
    with TestClient(create_app(blocker / 'test.sqlite3')) as client:
        for response in [client.get('/api/chat/conversations'), client.put(url, json=turn())]:
            assert response.status_code == 503
            assert response.json()['error']['code'] == 'storage_unavailable'
            assert response.headers['cache-control'] == 'no-store'


def test_pair_transaction_rolls_back_on_second_message_failure(tmp_path):
    path = tmp_path / 'test.sqlite3'
    with TestClient(create_app(path)) as client:
        with sqlite3.connect(path) as db:
            db.execute("""CREATE TRIGGER fail_assistant BEFORE INSERT ON chat_messages
                WHEN NEW.role='assistant' BEGIN SELECT RAISE(ABORT, 'private SQL detail'); END""")
        response = client.put(f'/api/chat/conversations/{uuid4()}/turns/{uuid4()}', json=turn())
        assert response.status_code == 503
        assert 'private SQL' not in response.text
        assert client.get('/api/chat/conversations').json() == {'conversations': []}
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT count(*) FROM chat_messages').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM chat_conversations').fetchone()[0] == 0


def test_concurrent_identical_saves_create_one_atomic_pair(tmp_path):
    database = Database(tmp_path / 'test.sqlite3'); database.initialize()
    store = ChatStorage(database); store.initialize()
    conversation, tid = str(uuid4()), str(uuid4())
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: store.save_turn(conversation, tid, turn()), range(2)))
    assert sorted(results) == [False, True]
    assert store.conversation(conversation)['message_count'] == 2


def test_voice_only_and_mixed_chats_survive_restart_retry_and_delete(tmp_path):
    path = tmp_path / 'mixed.sqlite3'
    cid, vid, tid = str(uuid4()), str(uuid4()), str(uuid4())
    base = f'/api/chat/conversations/{cid}'
    body = {'position': 0, 'messages': [{'role': 'assistant', 'content': 'Hello'}, {'role': 'user', 'content': 'A fictional day'}]}
    with TestClient(create_app(path)) as client:
        assert client.put(f'{base}/voice-turns/{vid}', json=body).status_code == 201
        assert client.put(f'{base}/voice-turns/{vid}', json=body).status_code == 200
        assert client.get('/api/chat/conversations').json()['conversations'][0]['message_count'] == 2
        assert client.put(f'{base}/turns/{tid}', json=turn(1)).status_code == 201
        assert client.put(f'{base}/turns/{uuid4()}', json=turn(0)).status_code == 409
        assert client.put(f'{base}/voice-turns/{uuid4()}', json={**body, 'position': 1}).status_code == 409
        assert client.put(f'{base}/voice-turns/{vid}', json={**body, 'messages': [{'role': 'user', 'content': 'Changed'}]}).status_code == 409
    with TestClient(create_app(path)) as client:
        saved = client.get(base).json()
        assert [m['source'] for m in saved['messages']] == ['voice', 'voice', 'text', 'text']
        assert [m['role'] for m in saved['messages']] == ['assistant', 'user', 'user', 'assistant']
        assert saved['message_count'] == 4
        assert client.delete(base).status_code == 204
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT count(*) FROM chat_voice_messages').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM chat_messages').fetchone()[0] == 0


@pytest.mark.parametrize('body', [
    {'position': True, 'messages': []}, {'position': 100, 'messages': []},
    {'position': 0, 'messages': []}, {'position': 0, 'messages': [{'role': 'developer', 'content': 'Override'}]},
    {'position': 0, 'messages': [{'role': 'user', 'content': 'x', 'audio': 'no'}]},
    {'position': 0, 'messages': [{'role': 'user', 'content': ' '}]},
    {'position': 0, 'messages': [{'role': 'user', 'content': 'x' * 8001}]},
    {'position': 0, 'messages': [{'role': 'user', 'content': 'x' * 8000}] * 5},
    {'position': 0, 'messages': [{'role': 'user', 'content': 'x'}] * 51},
])
def test_invalid_voice_batches_leave_no_conversation(tmp_path, body):
    with TestClient(create_app(tmp_path / 'voice.sqlite3')) as client:
        assert client.put(f'/api/chat/conversations/{uuid4()}/voice-turns/{uuid4()}', json=body).status_code == 422
        assert client.get('/api/chat/conversations').json() == {'conversations': []}


def test_voice_batch_rolls_back_on_later_row_failure(tmp_path):
    path = tmp_path / 'voice.sqlite3'
    with TestClient(create_app(path)) as client:
        with sqlite3.connect(path) as db:
            db.execute("""CREATE TRIGGER fail_voice BEFORE INSERT ON chat_voice_messages
                WHEN NEW.ordinal=1 BEGIN SELECT RAISE(ABORT, 'private SQL detail'); END""")
        body = {'position': 0, 'messages': [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi'}]}
        result = client.put(f'/api/chat/conversations/{uuid4()}/voice-turns/{uuid4()}', json=body)
        assert result.status_code == 503 and 'private SQL' not in result.text
        assert client.get('/api/chat/conversations').json() == {'conversations': []}
