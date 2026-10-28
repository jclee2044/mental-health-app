"""Feature-local bounded JSON parsing, shared by the voice and typed routes."""
import json
from .domain import MAX_BODY_BYTES


class RequestTooLarge(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError()
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError()


async def read_json(request):
    length = request.headers.get("content-length")
    if length is not None:
        length = int(length)
        if length < 0:
            raise ValueError()
        if length > MAX_BODY_BYTES:
            raise RequestTooLarge()
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_BODY_BYTES:
            raise RequestTooLarge()
        chunks.append(chunk)
    return json.loads(b"".join(chunks), object_pairs_hook=unique_object, parse_constant=reject_constant)
