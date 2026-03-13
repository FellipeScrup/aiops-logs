from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.schemas import DiagnoseResponse, LogIngestRequest
from app.db.postgres import insert_diagnosis, insert_silver_log
from app.services.milvus_service import search_context
from app.services.mlflow_service import log_diagnosis_experiment
from app.services.minio_service import save_json_to_minio
from app.services.ollama_service import generate_embedding, run_diagnosis
from app.services.silver_service import normalize_to_silver


async def run_full_diagnosis(log: LogIngestRequest) -> DiagnoseResponse:
    silver = normalize_to_silver(log)

    # Bronze: armazena payload bruto no data lake
    save_json_to_minio(
        bucket_name=settings.minio_bucket_bronze,
        payload=log.model_dump(),
        prefix=f"{silver.source}/{silver.level.lower()}",
    )

    # Silver: padroniza e persiste no relacional
    silver_log_id = insert_silver_log(silver.model_dump())
    save_json_to_minio(
        bucket_name=settings.minio_bucket_silver,
        payload=silver.model_dump(),
        prefix=f"{silver.source}/{silver.level.lower()}",
    )

    query_embedding = await generate_embedding(silver.message)
    context_items = search_context(query_embedding=query_embedding, limit=3)
    context_texts = [item.get("content", "") for item in context_items if item.get("content")]

    diagnosis_payload, response_time_ms = await run_diagnosis(
        log_text=silver.message,
        context_chunks=context_texts,
    )

    diagnosis_payload.setdefault("diagnosis", "Unknown root cause")
    diagnosis_payload.setdefault("suggested_fix", "Collect more logs and inspect dependencies")
    diagnosis_payload.setdefault("confidence", 0.2)

    insert_diagnosis(
        silver_log_id=silver_log_id,
        model=settings.ollama_chat_model,
        response_time_ms=response_time_ms,
        diagnosis_payload=diagnosis_payload,
    )

    log_diagnosis_experiment(
        model_name=settings.ollama_chat_model,
        source=silver.source,
        level=silver.level,
        response_time_ms=response_time_ms,
        has_context=bool(context_items),
        diagnosis_payload=diagnosis_payload,
    )

    return DiagnoseResponse(
        silver_log_id=silver_log_id,
        diagnosis=str(diagnosis_payload["diagnosis"]),
        suggested_fix=str(diagnosis_payload["suggested_fix"]),
        confidence=float(diagnosis_payload["confidence"]),
        context=context_items,
        model=settings.ollama_chat_model,
        response_time_ms=response_time_ms,
    )
