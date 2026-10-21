"""HTTP shapes only; semantic validation belongs to domain.py."""
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr


class EntryBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feeling: StrictInt
    color: StrictStr
    color_meaning: StrictStr = ""
    pleasantness: StrictInt
    energy: StrictInt
    note: StrictStr = ""
    recorded_at: StrictStr
    local_date: StrictStr
