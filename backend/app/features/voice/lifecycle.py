"""Process-local session IDs/close outcomes only; never audio or transcripts."""
from threading import Lock


class UnknownSession(ValueError):
    pass


class SessionClosures:
    def __init__(self):
        self._states = {}
        self._lock = Lock()

    def remember(self, session_id):
        with self._lock:
            if session_id in self._states:
                raise ValueError("Session ID was reused")
            self._states[session_id] = "open"

    def begin(self, session_id):
        with self._lock:
            if session_id not in self._states:
                raise UnknownSession()
            state = self._states[session_id]
            if state == "open":
                self._states[session_id] = "closing"
            return state

    def finish(self, session_id, succeeded):
        with self._lock:
            self._states[session_id] = "closed" if succeeded else "failed"
