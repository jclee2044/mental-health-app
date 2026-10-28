"""Single bounded HTTP attempt using the standard library; no SDK or retries."""
import json
import secrets
from http.client import HTTPException as TransportError
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from .domain import MAX_PROVIDER_BYTES, InvalidProviderResponse, validate_provider_response, validate_text_response
from .prompts import BACKEND_INSTRUCTIONS
from .lifecycle import SessionClosures
from .settings import PROVIDER_TIMEOUT_SECONDS, PROVIDER_URL, session_payload
from .dictation_domain import transcript_text


class ProviderUnavailable(Exception):
    pass


class ProviderTimeout(ProviderUnavailable):
    pass


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not replay a creation POST or forward credentials to another URL.
        return None


def open_provider_request(request, *, timeout):
    return build_opener(NoRedirects()).open(request, timeout=timeout)


class LiveProvider:
    def __init__(self, settings):
        self.settings = settings
        self.closures = SessionClosures()

    def create_session(self, sdp, history=()):
        session_id, answer = validate_provider_response(self._post(PROVIDER_URL, session_payload(sdp, self.settings.backend_model, history), 201))
        try:
            self.closures.remember(session_id)
        except ValueError:
            raise InvalidProviderResponse() from None
        return session_id, answer

    def end_session(self, session_id):
        state = self.closures.begin(session_id)
        if state in {"closed", "closing"}:
            return state
        if state == "failed":
            raise ProviderUnavailable()
        try:
            self._post(f"{PROVIDER_URL}/{session_id}/hangup", {}, (200, 204), timeout=3)
        except Exception:
            self.closures.finish(session_id, False)
            raise
        self.closures.finish(session_id, True)
        return "closed"

    def reply_text(self, message, history):
        data = self._post("https://api.openai.com/v1/responses", {
            "model": self.settings.backend_model,
            "instructions": BACKEND_INSTRUCTIONS + "\nFor this typed turn, reply to the user in text, following the conversation policy above.",
            "input": [*history, {"role": "user", "content": message}],
            "store": False, "tools": [], "tool_choice": "none", "max_output_tokens": 1024,
        }, 200)
        return validate_text_response(data)

    def transcribe(self, audio, mime, extension):
        boundary = "dictation_" + secrets.token_hex(16)
        fields = [
            f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\ngpt-transcribe\r\n'.encode(),
            f'--{boundary}\r\nContent-Disposition: form-data; name="response_format"\r\n\r\njson\r\n'.encode(),
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="dictation.{extension}"\r\nContent-Type: {mime}\r\n\r\n'.encode(),
            audio, f'\r\n--{boundary}--\r\n'.encode(),
        ]
        result = self._post("https://api.openai.com/v1/audio/transcriptions", b"".join(fields), 200,
                            timeout=20, content_type=f"multipart/form-data; boundary={boundary}")
        try:
            return transcript_text(result)
        except (ValueError, UnicodeError):
            raise InvalidProviderResponse() from None

    def _post(self, url, payload, success_status, *, timeout=PROVIDER_TIMEOUT_SECONDS, content_type="application/json"):
        request = Request(
            url,
            data=payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.settings.api_key}", "Content-Type": content_type, "Accept": "application/json"},
            method="POST",
        )
        try:
            with open_provider_request(request, timeout=timeout) as response:
                statuses = success_status if isinstance(success_status, tuple) else (success_status,)
                if response.status not in statuses:
                    raise ProviderUnavailable()
                if success_status == (200, 204):
                    return None
                if response.headers.get_content_type() != "application/json":
                    raise InvalidProviderResponse()
                raw = response.read(MAX_PROVIDER_BYTES + 1)
                if len(raw) > MAX_PROVIDER_BYTES:
                    raise InvalidProviderResponse()
                try:
                    result = json.loads(raw)
                except (ValueError, UnicodeError, RecursionError):
                    raise InvalidProviderResponse() from None
                return result
        except HTTPError as error:
            error.close()
            raise ProviderUnavailable() from None
        except TimeoutError:
            raise ProviderTimeout() from None
        except URLError as error:
            if isinstance(error.reason, TimeoutError):
                raise ProviderTimeout() from None
            raise ProviderUnavailable() from None
        except (OSError, TransportError, ValueError) as error:
            if isinstance(error, InvalidProviderResponse):
                raise InvalidProviderResponse() from None
            raise ProviderUnavailable() from None
