from fastapi import FastAPI

from app.routes.logs import router as logs_router


def create_app() -> FastAPI:
    app = FastAPI(title="AIOps Log Ingestion API", version="1.0.0")
    app.include_router(logs_router)
    return app


app = create_app()
