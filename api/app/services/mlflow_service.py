from __future__ import annotations

from typing import Any

import mlflow

from app.core.config import settings


def log_diagnosis_experiment(
    *,
    model_name: str,
    source: str,
    level: str,
    response_time_ms: int,
    has_context: bool,
    diagnosis_payload: dict[str, Any],
) -> None:
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    with mlflow.start_run():
        mlflow.log_param("model", model_name)
        mlflow.log_param("source", source)
        mlflow.log_param("level", level)
        mlflow.log_param("has_context", has_context)
        mlflow.log_metric("response_time_ms", float(response_time_ms))
        mlflow.log_metric("confidence", float(diagnosis_payload.get("confidence", 0.0)))
        mlflow.log_dict(diagnosis_payload, "diagnosis.json")
