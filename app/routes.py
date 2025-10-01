from fastapi import APIRouter, UploadFile, File, HTTPException
import os, uuid
from app.storage import JobStorage
from app.evaluator import Evaluator
from PyPDF2 import PdfReader
from fastapi import Query

router = APIRouter()
storage = JobStorage("jobs.db")
evaluator = Evaluator()
jobs = {}  # job_id -> {"file_path": ..., "result": ..., "status": ...}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

@router.post("/upload")
async def upload_cv(file: UploadFile):
    job_id = str(uuid.uuid4())
    file_path = f"uploads/{job_id}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    jobs[job_id] = {"file_path": file_path, "status": "uploaded", "result": None}
    return {"job_id": job_id, "cv_path": file_path, "status": "uploaded"}

def extract_text_from_pdf(path: str, max_chars: int = 4000) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    text = text.strip()

    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Truncated due to length]"

    return text

@router.post("/evaluate")
async def evaluate_cv(job_id: str = Query(...)):
    if job_id not in jobs:
        return {"error": "job_id not found"}

    file_path = jobs[job_id]["file_path"]
    try:
        cv_text = evaluator.extract_text_from_pdf(file_path)
        result = evaluator.evaluate_text(cv_text)
        jobs[job_id]["result"] = result
        jobs[job_id]["status"] = "completed"
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        return {"error": str(e), "status": "failed"}

    return {"job_id": job_id, "result": result, "status": "completed"}