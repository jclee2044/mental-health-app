"""Bounded, framework-free dictation audio and transcript validation."""
import base64
import binascii

MAX_AUDIO_BYTES = 2 * 1024 * 1024
MAX_DICTATION_BODY = 3 * 1024 * 1024
AUDIO_FORMATS = {"audio/webm": "webm", "audio/mp4": "mp4"}


def decode_audio(data):
    if not isinstance(data, dict) or set(data) != {"audio", "mime_type"}:
        raise ValueError()
    mime = data["mime_type"]
    if not isinstance(mime, str) or mime not in AUDIO_FORMATS:
        raise ValueError()
    encoded = data["audio"]
    if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_AUDIO_BYTES + 2) // 3):
        raise ValueError()
    try:
        audio = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError() from None
    if not audio or len(audio) > MAX_AUDIO_BYTES:
        raise ValueError()
    if mime == "audio/webm" and not audio.startswith(b"\x1a\x45\xdf\xa3"):
        raise ValueError()
    if mime == "audio/mp4" and (len(audio) < 12 or audio[4:8] != b"ftyp"):
        raise ValueError()
    return audio, mime, AUDIO_FORMATS[mime]


def transcript_text(data):
    text = data.get("text") if isinstance(data, dict) else None
    if not isinstance(text, str) or not text.strip() or len(text) > 4000 or len(text.encode("utf-8")) > 8000:
        raise ValueError()
    return text.strip()
