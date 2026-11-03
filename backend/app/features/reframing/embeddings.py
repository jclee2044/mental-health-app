"""Explicitly constructed, bounded embedding adapter. No default model or retries."""
import json
from http.client import HTTPException as TransportError
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from .domain import InvalidKnowledge, embedding_spec, strict_json, unit_vector

URL = "https://api.openai.com/v1/embeddings"
TIMEOUT_SECONDS = 5
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class EmbeddingUnavailable(Exception):
    pass


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_embedding_request(request, *, timeout):
    return build_opener(NoRedirects()).open(request, timeout=timeout)


class OpenAIEmbedder:
    def __init__(self, api_key, model, dimensions):
        self.spec = embedding_spec("openai", model, dimensions)
        if not isinstance(api_key, str) or not api_key or len(api_key) > 4096 or any(not 33 <= ord(c) <= 126 for c in api_key):
            raise InvalidKnowledge("Invalid embedding credential.")
        self._key = api_key

    def __repr__(self):
        return f"OpenAIEmbedder(model={self.spec['model']!r}, dimensions={self.spec['dimensions']})"

    def embed(self, inputs):
        if not isinstance(inputs, (list, tuple)) or not 1 <= len(inputs) <= 16:
            raise InvalidKnowledge("Embedding batch outside allowed bounds.")
        limit = 8000 if len(inputs) == 1 else 4000
        try:
            if any(not isinstance(t, str) or not t.strip() or len(t.encode('utf-8')) > limit for t in inputs) or sum(len(t.encode('utf-8')) for t in inputs) > 24000:
                raise InvalidKnowledge("Embedding text outside allowed bounds.")
        except UnicodeError as exc:
            raise InvalidKnowledge("Invalid embedding text.") from exc
        payload = {"model": self.spec["model"], "dimensions": self.spec["dimensions"], "input": list(inputs), "encoding_format": "float"}
        request = Request(URL, data=json.dumps(payload).encode(), method="POST", headers={
            "Authorization": f"Bearer {self._key}", "Content-Type": "application/json", "Accept": "application/json",
        })
        try:
            with open_embedding_request(request, timeout=TIMEOUT_SECONDS) as response:
                if response.status != 200 or response.headers.get_content_type() != "application/json":
                    raise EmbeddingUnavailable()
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise EmbeddingUnavailable()
                data = strict_json(raw)
            if not isinstance(data, dict) or data.get("model") != self.spec["model"]:
                raise EmbeddingUnavailable()
            records = data.get("data")
            if not isinstance(records, list) or len(records) != len(inputs):
                raise EmbeddingUnavailable()
            vectors = {}
            for record in records:
                if not isinstance(record, dict) or record.get("object") != "embedding":
                    raise EmbeddingUnavailable()
                index = record.get("index")
                if type(index) is not int or not 0 <= index < len(inputs) or index in vectors:
                    raise EmbeddingUnavailable()
                vectors[index] = unit_vector(record.get("embedding"), self.spec["dimensions"])
            return tuple(vectors[i] for i in range(len(inputs)))
        except HTTPError as exc:
            exc.close()
            raise EmbeddingUnavailable("Embedding service unavailable.") from None
        except (URLError, OSError, TransportError, ValueError, TypeError, KeyError, EmbeddingUnavailable):
            raise EmbeddingUnavailable("Embedding service unavailable.") from None
