from __future__ import annotations

from app.core.schemas import LogIngestRequest, SilverLogRecord


def extract_stacktrace(message: str) -> str | None:
    markers = ["Traceback", "Exception", "Error:", "at "]
    has_stacktrace = any(marker in message for marker in markers)
    if not has_stacktrace:
        return None

    lines = [line.strip() for line in message.splitlines() if line.strip()]
    stacktrace_lines = [line for line in lines if " at " in line or "File " in line or "Error" in line]
    if stacktrace_lines:
        return "\n".join(stacktrace_lines)

    return message


def normalize_to_silver(log: LogIngestRequest) -> SilverLogRecord:
    return SilverLogRecord(
        source=log.source.lower().strip(),
        level=log.level.upper().strip(),
        message=log.message.strip(),
        timestamp=log.timestamp,
        stacktrace=extract_stacktrace(log.message),
        raw_payload=log.model_dump(),
    )
