from __future__ import annotations

import io
import json
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from minio import Minio

from app.core.config import settings


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket_exists(bucket_name: str) -> None:
    client = get_minio_client()
    if client.bucket_exists(bucket_name):
        return
    client.make_bucket(bucket_name)


def save_json_to_minio(bucket_name: str, payload: dict[str, Any], prefix: str) -> str:
    ensure_bucket_exists(bucket_name)
    object_name = (
        f"{prefix}/{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
    )
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    payload_stream = io.BytesIO(payload_bytes)

    get_minio_client().put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=payload_stream,
        length=len(payload_bytes),
        content_type="application/json",
    )
    return object_name
