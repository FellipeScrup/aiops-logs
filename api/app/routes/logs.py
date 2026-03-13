from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.core import diagnose_log
from app.core.schemas import DiagnoseResponse, LogIngestRequest
from app.services.minio_service import save_json_to_minio

router = APIRouter(prefix="", tags=["logs"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ingest")
async def ingest_log(log: LogIngestRequest) -> dict[str, str]:
    try:
        object_name = save_json_to_minio(
            bucket_name=settings.minio_bucket_bronze,
            payload=log.model_dump(),
            prefix=f"{log.source.lower()}/{log.level.lower()}",
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Bronze ingest failed: {exc}") from exc

    return {
        "status": "success",
        "bucket": settings.minio_bucket_bronze,
        "object": object_name,
    }


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(log: LogIngestRequest) -> DiagnoseResponse:
    try:
        return await diagnose_log(log)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Diagnosis pipeline failed: {exc}") from exc
