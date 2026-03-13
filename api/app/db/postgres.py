from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
import psycopg2.extras

from app.core.config import settings


@contextmanager
def get_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    connection = psycopg2.connect(settings.postgres_dsn)
    try:
        yield connection
    finally:
        connection.close()


def init_tables() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS silver_logs (
                    id BIGSERIAL PRIMARY KEY,
                    source TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMPTZ,
                    stacktrace TEXT,
                    raw_payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS diagnostics (
                    id BIGSERIAL PRIMARY KEY,
                    silver_log_id BIGINT REFERENCES silver_logs(id),
                    model TEXT NOT NULL,
                    response_time_ms INTEGER NOT NULL,
                    diagnosis JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
        connection.commit()


def insert_silver_log(record: dict[str, Any]) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO silver_logs (source, level, message, timestamp, stacktrace, raw_payload)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    record["source"],
                    record["level"],
                    record["message"],
                    record["timestamp"],
                    record.get("stacktrace"),
                    psycopg2.extras.Json(record["raw_payload"]),
                ),
            )
            new_id = cursor.fetchone()[0]
        connection.commit()
    return int(new_id)


def insert_diagnosis(
    silver_log_id: int,
    model: str,
    response_time_ms: int,
    diagnosis_payload: dict[str, Any],
) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO diagnostics (silver_log_id, model, response_time_ms, diagnosis)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    silver_log_id,
                    model,
                    response_time_ms,
                    json.dumps(diagnosis_payload),
                ),
            )
            new_id = cursor.fetchone()[0]
        connection.commit()
    return int(new_id)
