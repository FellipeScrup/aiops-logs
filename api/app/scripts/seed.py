from __future__ import annotations

from app.core.config import settings
from app.db.postgres import init_tables
from app.services.milvus_service import ensure_collection_exists
from app.services.minio_service import ensure_bucket_exists


def run_seed() -> None:
    ensure_bucket_exists(settings.minio_bucket_bronze)
    ensure_bucket_exists(settings.minio_bucket_silver)
    ensure_bucket_exists("mlflow")

    init_tables()
    ensure_collection_exists()


if __name__ == "__main__":
    run_seed()
    print("Seed concluido com sucesso.")
