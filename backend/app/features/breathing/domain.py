"""Fixed-pattern session record checks, independent of HTTP and SQLite."""
from datetime import datetime
from math import isfinite
from ...errors import ValidationError


def validate_session(payload):
    fields = {}
    if payload.get("pattern") != "paced-4-6-v1":
        fields["pattern"] = "Use the fixed four-in/six-out pattern."
    if payload.get("status") not in ("completed", "ended"):
        fields["status"] = "Use completed or ended."
    for key in ("sequence_seconds", "active_seconds", "pause_seconds", "instruction_seconds"):
        value = payload.get(key)
        if type(value) not in (int, float) or not isfinite(value) or value < 0:
            fields[key] = "Use a finite nonnegative duration."
    if not any(key.endswith("seconds") for key in fields):
        sequence, active = payload["sequence_seconds"], payload["active_seconds"]
        if sequence > 63 or active > 60 or abs(active - max(0, sequence - 3)) > .05:
            fields["active_seconds"] = "Duration must match the fixed sequence."
        if payload["status"] == "completed" and (abs(sequence - 63) > .05 or abs(active - 60) > .05):
            fields["status"] = "Completion requires all six cycles."
        if payload["instruction_seconds"] + .05 < sequence:
            fields["instruction_seconds"] = "Include the complete guided sequence."
    try:
        started = datetime.fromisoformat(payload["started_at"].replace("Z", "+00:00"))
        ended = datetime.fromisoformat(payload["ended_at"].replace("Z", "+00:00"))
        if started.utcoffset() is None or ended.utcoffset() is None or ended < started:
            raise ValueError()
        from datetime import date
        local_day = date.fromisoformat(payload["local_date"])
        if abs((local_day - started.date()).days) > 1:
            raise ValueError()
    except (ValueError, KeyError, TypeError, AttributeError):
        fields["started_at"] = "Use ordered timestamps with offsets and a valid local date."
    if fields:
        raise ValidationError(fields)
    return payload
