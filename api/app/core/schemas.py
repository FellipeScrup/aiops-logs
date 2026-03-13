from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogIngestRequest(BaseModel):
    source: str = Field(..., examples=["frontend"])
    level: str = Field(..., examples=["ERROR"])
    message: str = Field(..., examples=["TypeError: Cannot read property 'id' of undefined"])
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SilverLogRecord(BaseModel):
    source: str
    level: str
    message: str
    timestamp: str
    stacktrace: str | None = None
    raw_payload: dict[str, Any]


class DiagnoseResponse(BaseModel):
    silver_log_id: int
    diagnosis: str
    suggested_fix: str
    confidence: float
    context: list[dict[str, Any]]
    model: str
    response_time_ms: int
