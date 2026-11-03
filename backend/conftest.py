"""Routine verification must never inherit an enabled paid lookup or use network."""
import pytest


@pytest.fixture(autouse=True)
def isolated_provider_environment(monkeypatch):
    monkeypatch.setenv('REFRAMING_ENABLED', '0')
    monkeypatch.delenv('CHAT_REASONING_EFFORT', raising=False)
    def forbidden(*args, **kwargs):
        raise AssertionError('External HTTP is forbidden in routine tests')
    monkeypatch.setattr('http.client.HTTPConnection.connect', forbidden)
    monkeypatch.setattr('http.client.HTTPSConnection.connect', forbidden)
