"""Neutral source-data envelope; no feature dependencies or transport logic."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBlock:
    policy: str = ""
    data: str = ""


@dataclass(frozen=True)
class TurnContext:
    personal: ContextBlock = ContextBlock()
    techniques: ContextBlock = ContextBlock()
    personal_report: dict | None = None
    technique_report: dict | None = None
