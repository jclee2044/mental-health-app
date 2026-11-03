"""Actual bundled definitions + fake SDP/provider; no embeddings or microphone."""
import asyncio
import json
from datetime import date
from uuid import uuid4
import pytest
from app.features.reframing import catalogue
from app.features.reframing.corpus import load_corpus
from app.features.reframing.domain import InvalidKnowledge
from test_voice import client, SDP, FakeResponse, valid_response


def install(browser):
    async def prepare(history_bytes):
        return await catalogue.prepare_catalogue(history_bytes, enabled=True)
    browser.app.state.prepare_voice_catalogue = prepare


def test_catalogue_has_every_active_operation_boundaries_and_only_real_sources():
    corpus = load_corpus()
    block, report = catalogue.catalogue_block(corpus)
    data = json.loads(block.data.split('\n', 1)[1])
    assert len(data['cards']) == 19 and len(report['card_ids']) == 19
    assert set(report['card_ids']) == {card['id'] for card in corpus.active}
    originals = {card['id']: card for card in corpus.active}
    for card in data['cards']:
        assert card['operation'] == originals[card['id']]['operation']
        assert card['avoid'] == originals[card['id']]['avoid']
        assert {data['sources'][i]['id'] for i in card['sources']} == {r['source_id'] for r in originals[card['id']]['sources']}
    assert data['corpus_sha256'] == corpus.fingerprint
    assert len(block.data.encode()) < catalogue.MAX_STARTUP_CONTENT_BYTES
    with pytest.raises(InvalidKnowledge):
        catalogue.catalogue_block(corpus, 6000)


def test_disabled_catalogue_never_reads_corpus(monkeypatch):
    def forbidden():
        pytest.fail('Disabled catalogue performed I/O')
    monkeypatch.setattr(catalogue, 'load_corpus', forbidden)
    block, report = asyncio.run(catalogue.prepare_catalogue(0))
    assert not block.data and report is None


def test_voice_receives_source_data_and_preserves_history_without_embeddings(client):
    browser, sender = client
    install(browser)
    sender.side_effect = None; sender.return_value = FakeResponse(valid_response())
    history = [{'role': 'user', 'content': 'Fictional graduation plans.'}]
    response = browser.post('/api/voice/sessions', json={'sdp': SDP, 'history': history})
    assert response.status_code == 201
    assert response.json()['reframing']['delivery'] == 'startup_catalogue'
    assert len(response.json()['reframing']['card_ids']) == 19
    session = json.loads(sender.call_args.args[0].data)['session']
    reference = session['input'][0]
    assert reference['role'] == 'user'
    data = json.loads(reference['content'][0]['text'].split('\n', 1)[1])
    assert len(data['cards']) == 19
    assert session['input'][1]['content'][0]['text'] == 'Fictional graduation plans.'
    operation = next(card['operation'] for card in data['cards'] if card['id'] == 'counterexample')
    assert operation not in session['instructions']
    assert operation not in session['delegation']['responses']['instructions']
    assert 'startup catalogue' in session['instructions']
    assert session['client']['data_channel']['allowed_client_events'] == ['session.close']
    assert session['delegation']['responses']['tools'] == [] and session['store'] is False
    sender.assert_called_once()


def test_personal_snapshot_never_becomes_catalogue_content(client):
    browser, sender = client
    install(browser)
    browser.put('/api/personal-memory/preferences', json={'emotions': False, 'conversations': False, 'facts': True})
    browser.put(f'/api/personal-memory/facts/{uuid4()}', json={'text': 'A fictional private preference.'})
    sender.side_effect = None; sender.return_value = FakeResponse(valid_response())
    response = browser.post('/api/voice/sessions', json={'sdp': SDP, 'personal_memory': {
        'local_date': date.today().isoformat(), 'conversation_id': str(uuid4())}})
    assert response.status_code == 201
    session = json.loads(sender.call_args.args[0].data)['session']
    assert 'A fictional private preference.' in session['instructions']
    assert 'A fictional private preference.' not in session['input'][0]['content'][0]['text']
    assert response.json()['personal_memory']['status'] == 'ready'
    sender.assert_called_once()


def test_long_history_is_preserved_and_catalogue_failure_is_visible(client):
    browser, sender = client
    install(browser)
    sender.side_effect = None; sender.return_value = FakeResponse(valid_response())
    text = 'x' * 6000
    response = browser.post('/api/voice/sessions', json={'sdp': SDP, 'history': [{'role': 'user', 'content': text}]})
    assert response.status_code == 201 and response.json()['reframing']['status'] == 'unavailable'
    session = json.loads(sender.call_args.args[0].data)['session']
    assert len(session['input']) == 1 and session['input'][0]['content'][0]['text'] == text
    sender.assert_called_once()


def test_bad_corpus_does_not_block_voice_or_send_partial_catalogue(client, monkeypatch):
    browser, sender = client
    install(browser)
    def broken():
        raise InvalidKnowledge('private detail')
    monkeypatch.setattr(catalogue, 'load_corpus', broken)
    sender.side_effect = None; sender.return_value = FakeResponse(valid_response())
    response = browser.post('/api/voice/sessions', json={'sdp': SDP})
    assert response.status_code == 201 and response.json()['reframing']['status'] == 'unavailable'
    assert 'private detail' not in response.text
    assert json.loads(sender.call_args.args[0].data)['session']['input'] == []


def test_browser_cannot_supply_its_own_catalogue(client):
    browser, sender = client
    assert browser.post('/api/voice/sessions', json={'sdp': SDP, 'reframing': {'cards': []}}).status_code == 422
    sender.assert_not_called()
