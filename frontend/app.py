from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import gradio as gr
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


async def analyze_log(source: str, level: str, message: str) -> str:
    payload = {
        "source": source,
        "level": level,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{API_BASE_URL}/diagnose", json=payload)
        response.raise_for_status()
        diagnosis = response.json()

    return json.dumps(diagnosis, indent=2, ensure_ascii=False)


with gr.Blocks(title="AIOps Diagnostics") as app:
    gr.Markdown("# AIOps Diagnostics\nCole o log e receba o diagnóstico via RAG + LLM local.")

    source_input = gr.Dropdown(
        choices=["frontend", "backend", "infra"],
        value="backend",
        label="Fonte",
    )
    level_input = gr.Dropdown(
        choices=["ERROR", "WARNING", "INFO"],
        value="ERROR",
        label="Nível",
    )
    message_input = gr.Textbox(lines=12, label="Log", placeholder="Cole aqui o stacktrace ou erro...")

    analyze_button = gr.Button("Analisar")
    output = gr.Code(label="Diagnóstico", language="json")

    analyze_button.click(analyze_log, inputs=[source_input, level_input, message_input], outputs=output)


if __name__ == "__main__":
    app.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    )
