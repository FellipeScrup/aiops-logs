from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings


async def generate_embedding(text: str) -> list[float]:
    url = f"{settings.ollama_base_url}/api/embeddings"
    payload = {"model": settings.ollama_embed_model, "prompt": text}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        body = response.json()

    vector = body.get("embedding", [])
    if not isinstance(vector, list) or not vector:
        raise ValueError("Ollama embedding response is empty or invalid")

    return [float(v) for v in vector]


async def run_diagnosis(log_text: str, context_chunks: list[str]) -> tuple[dict[str, Any], int]:
    context_block = "\n\n".join(context_chunks) if context_chunks else "No relevant context found in vector DB."
    prompt = (
        "You are an AIOps assistant. Analyze the error log and return a JSON object with keys: "
        "diagnosis, suggested_fix, confidence. Confidence must be a number between 0 and 1.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Log:\n{log_text}"
    )

    url = f"{settings.ollama_base_url}/api/chat"
    payload = {
        "model": settings.ollama_chat_model,
        "stream": False,
        "format": "json",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        body = response.json()

    message_content = body.get("message", {}).get("content", "{}")
    diagnosis_payload = json.loads(message_content)

    total_duration = int(body.get("total_duration", 0))
    response_time_ms = max(total_duration // 1_000_000, 1)

    return diagnosis_payload, response_time_ms
