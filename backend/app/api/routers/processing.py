from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.documents import JobDescriptionRequest, ProcessedOutput
from app.services.pipeline import process_job_description_text, process_resume_file

router = APIRouter(prefix="/process", tags=["processing"])


@router.post("/resume", response_model=ProcessedOutput)
async def process_resume(file: UploadFile = File(...)) -> ProcessedOutput:
    try:
        return await process_resume_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/job-description", response_model=ProcessedOutput)
def process_job_description(payload: JobDescriptionRequest) -> ProcessedOutput:
    try:
        return process_job_description_text(payload.text, payload.options)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
