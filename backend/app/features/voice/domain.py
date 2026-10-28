"""Framework-free bounds and structural checks, not a full SDP negotiation parser."""
import re

MAX_SDP_BYTES = 64 * 1024
MAX_BODY_BYTES = 96 * 1024
MAX_PROVIDER_BYTES = 128 * 1024


def validate_saved_turn(values):
    """The browser saves completed typed pairs; never arbitrary roles/settings."""
    if type(values["position"]) is not int or not 0 <= values["position"] <= 99:
        raise ValueError()
    for role in ("user", "assistant"):
        text = values[role]
        if not isinstance(text, str) or not text.strip() or len(text.encode("utf-8")) > 8000:
            raise ValueError()
    return values


def validate_saved_voice(values):
    if type(values["position"]) is not int or not 0 <= values["position"] <= 99:
        raise ValueError()
    messages = values["messages"]
    if not 1 <= len(messages) <= 50:
        raise ValueError()
    sizes = []
    for message in messages:
        if message["role"] not in {"user", "assistant"} or not message["content"].strip():
            raise ValueError()
        sizes.append(len(message["content"].encode("utf-8")))
    if any(size > 8000 for size in sizes) or sum(sizes) > 32000:
        raise ValueError()
    return values


class InvalidSdp(ValueError):
    pass


class OversizedSdp(InvalidSdp):
    pass


class InvalidProviderResponse(ValueError):
    pass


def validate_sdp(sdp):
    if not isinstance(sdp, str):
        raise InvalidSdp()
    try:
        size = len(sdp.encode("utf-8"))
    except UnicodeError:
        raise InvalidSdp() from None
    if size > MAX_SDP_BYTES:
        raise OversizedSdp()
    if any((ord(char) < 32 and char not in "\r\n\t") or ord(char) == 127 for char in sdp):
        raise InvalidSdp()
    lines = sdp.replace("\r\n", "\n").splitlines()
    if not lines or lines[0] != "v=0" or "\r" in sdp.replace("\r\n", ""):
        raise InvalidSdp()
    if any(not re.fullmatch(r"[a-z]=[^\r\n]+", line) for line in lines):
        raise InvalidSdp()
    if not all(any(line.startswith(prefix) for line in lines) for prefix in ("o=", "s=", "t=", "m=audio ")):
        raise InvalidSdp()
    return sdp


def validate_provider_response(data):
    if not isinstance(data, dict):
        raise InvalidProviderResponse()
    session, transport = data.get("session"), data.get("transport")
    if not isinstance(session, dict) or not isinstance(transport, dict):
        raise InvalidProviderResponse()
    session_id = session.get("id")
    if not isinstance(session_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", session_id):
        raise InvalidProviderResponse()
    if transport.get("type") != "webrtc":
        raise InvalidProviderResponse()
    try:
        sdp = validate_sdp(transport.get("sdp"))
    except InvalidSdp:
        raise InvalidProviderResponse() from None
    return session_id, sdp


def validate_history(history, max_bytes=32000):
    if len(history) > 16:
        raise ValueError()
    sizes = [len(item["content"].encode("utf-8")) for item in history]
    if any(item["role"] not in {"user", "assistant"} or not item["content"].strip() for item in history) or any(size > 8000 for size in sizes) or sum(sizes) > max_bytes:
        raise ValueError()
    return history


def validate_text_input(data):
    message = data["message"].strip()
    history = validate_history(data["history"])
    if not message or len(message.encode("utf-8")) > 8000:
        raise ValueError()
    return message, history


def validate_text_response(data):
    if not isinstance(data, dict) or data.get("status") != "completed" or not isinstance(data.get("output"), list):
        raise InvalidProviderResponse()
    parts = []
    for item in data["output"]:
        if not isinstance(item, dict):
            raise InvalidProviderResponse()
        if item.get("type") != "message":
            continue
        if item.get("role") != "assistant" or item.get("status") != "completed" or not isinstance(item.get("content"), list):
            raise InvalidProviderResponse()
        for part in item["content"]:
            if not isinstance(part, dict):
                raise InvalidProviderResponse()
            text = part.get("text") if part.get("type") == "output_text" else part.get("refusal") if part.get("type") == "refusal" else None
            if not isinstance(text, str):
                raise InvalidProviderResponse()
            parts.append(text)
    text = "\n".join(parts)
    try:
        if not text.strip() or len(text.encode("utf-8")) > 8000:
            raise InvalidProviderResponse()
    except UnicodeError:
        raise InvalidProviderResponse() from None
    return text
