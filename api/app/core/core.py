from app.core.schemas import DiagnoseResponse, LogIngestRequest
from app.services.diagnosis_service import run_full_diagnosis


async def diagnose_log(log: LogIngestRequest) -> DiagnoseResponse:
    return await run_full_diagnosis(log)
