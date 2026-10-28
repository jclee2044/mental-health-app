"""Entry rules. This module has no web framework or persistence imports."""
import re
from datetime import date, datetime, timezone


from ...errors import ValidationError


def validate_entry(payload):
    fields = {}
    for key, low, high, message in (
        ("pleasantness", -100, 100, "Choose pleasantness from −100 to 100."),
        ("energy", -100, 100, "Choose energy from −100 to 100."),
    ):
        value = payload.get(key)
        if type(value) is not int or not low <= value <= high:
            fields[key] = message
    feeling = payload.get("feeling")
    if feeling is not None and (type(feeling) is not int or not 1 <= feeling <= 5):
        fields["feeling"] = "Use a legacy feeling from 1 to 5, or null."
    if not isinstance(payload.get("color"), str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", payload["color"]):
        fields["color"] = "Choose a color."
    for key, limit in (("note", 2000), ("color_meaning", 80)):
        if not isinstance(payload.get(key, ""), str) or len(payload.get(key, "")) > limit:
            fields[key] = f"Use at most {limit} characters."
    try:
        timestamp = datetime.fromisoformat(payload["recorded_at"].replace("Z", "+00:00"))
        if timestamp.utcoffset() is None:
            raise ValueError()
        timestamp = timestamp.astimezone(timezone.utc)
    except (ValueError, KeyError, TypeError, AttributeError):
        fields["recorded_at"] = "Use a timestamp with a UTC offset."
    try:
        local_day = date.fromisoformat(payload["local_date"])
        if "recorded_at" not in fields and abs((local_day - timestamp.date()).days) > 1:
            raise ValueError()
    except (ValueError, KeyError, TypeError):
        fields["local_date"] = "Use the entry's local calendar date."
    if fields:
        raise ValidationError(fields)
    return {**payload, "feeling": feeling, "color": payload["color"].lower(), "note": payload.get("note", ""),
            "color_meaning": payload.get("color_meaning", ""), "recorded_at": timestamp.isoformat()}
