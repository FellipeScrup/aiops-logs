from __future__ import annotations

from time import sleep
from typing import Any

from pymilvus.exceptions import MilvusException

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.config import settings


MILVUS_DIMENSION = 768


def connect_milvus() -> None:
    last_error: Exception | None = None
    for _ in range(10):
        try:
            connections.connect(alias="default", uri=settings.milvus_uri, timeout=5.0)
            return
        except MilvusException as exc:
            last_error = exc
            sleep(2)

    raise RuntimeError(f"Could not connect to Milvus at {settings.milvus_uri}") from last_error


def ensure_collection_exists() -> None:
    last_error: Exception | None = None

    for _ in range(30):
        try:
            connect_milvus()
            if utility.has_collection(settings.milvus_collection, timeout=5.0):
                return

            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_DIMENSION),
            ]
            schema = CollectionSchema(fields=fields, description="AIOps RAG knowledge base")
            collection = Collection(name=settings.milvus_collection, schema=schema)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024},
            }
            collection.create_index(field_name="embedding", index_params=index_params, timeout=30.0)
            collection.load(timeout=30.0)
            return
        except MilvusException as exc:
            last_error = exc
            sleep(5)

    raise RuntimeError("Milvus proxy was not ready in time for seed") from last_error


def search_context(query_embedding: list[float], limit: int = 3) -> list[dict[str, Any]]:
    connect_milvus()
    if not utility.has_collection(settings.milvus_collection):
        return []

    collection = Collection(settings.milvus_collection)
    collection.load()

    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=limit,
        output_fields=["source", "content"],
    )

    parsed: list[dict[str, Any]] = []
    for hit in results[0]:
        entity = hit.entity
        parsed.append(
            {
                "score": float(hit.distance),
                "source": entity.get("source") if entity else "unknown",
                "content": entity.get("content") if entity else "",
            }
        )
    return parsed
