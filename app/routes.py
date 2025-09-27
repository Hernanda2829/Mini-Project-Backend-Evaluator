from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import uuid
import shutil
import os
from app.storage import JobStorage
from app.tasks import start_evaluation_job

router = APIRouter()

storage = JobStorage(db_path="jobs.db")

@router.post("/upload")
async def upload_files(cv: UploadFile = File(...), report: UploadFile = File(...)):
    # save files to uploads/
    uid = str(uuid.uuid4())
    base_dir = os.path.join("uploads", uid)
    os.makedirs(base_dir, exist_ok=True)

    cv_path = os.path.join(base_dir, f"cv_{cv.filename}")
    report_path = os.path.join(base_dir, f"report_{report.filename}")

    with open(cv_path, "wb") as f:
        shutil.copyfileobj(cv.file, f)
    with open(report_path, "wb") as f:
        shutil.copyfileobj(report.file, f)

    # create job record with uploaded files but no evaluation
    job_id = storage.create_job(cv_path=cv_path, report_path=report_path)
    return {"id": job_id, "status": "uploaded"}

@router.post("/evaluate")
async def evaluate(background_tasks: BackgroundTasks, job_id: str = None, temperature: float = 0.2):
    """
    Start evaluation for an existing upload job_id.
    If no job_id provided, it will create a new job (not recommended).
    temperature: control randomness for the mock LLM (0.0 - 1.0)
    """
    if job_id is None:
        raise HTTPException(status_code=400, detail="job_id required. Call /upload first.")
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    # change status to queued
    storage.update_status(job_id, "queued")
    # enqueue background worker
    background_tasks.add_task(start_evaluation_job, job_id, temperature)
    return {"id": job_id, "status": "queued"}

@router.get("/result/{job_id}")
async def get_result(job_id: str):
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    # return job status and result if completed
    result = job.get("result")
    return JSONResponse({"id": job_id, "status": job["status"], "result": result})
