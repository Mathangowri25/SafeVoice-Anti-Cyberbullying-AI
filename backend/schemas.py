from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ── Request sent TO the API ──────────────────────────
class ClassifyRequest(BaseModel):
    text:       str
    platform:   str = "unknown"
    user_id:    str = "anonymous"
    context_id: str = ""

# ── Response sent FROM the API ───────────────────────
class ClassifyResponse(BaseModel):
    text:       str
    label:      str
    severity:   int
    confidence: float
    scores:     dict
    alert_sent: bool

# ── Single incident from database ────────────────────
class IncidentOut(BaseModel):
    id:         int
    text:       str
    platform:   str
    label:      str
    severity:   int
    confidence: float
    alert_sent: bool
    reviewed:   bool
    timestamp:  datetime

    class Config:
        from_attributes = True   # lets SQLAlchemy model convert to this schema

# ── Update incident (moderator marks as reviewed) ────
class IncidentUpdate(BaseModel):
    reviewed: Optional[bool] = None