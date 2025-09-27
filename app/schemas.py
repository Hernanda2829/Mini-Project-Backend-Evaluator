# app/schemas.py
from pydantic import BaseModel

class EvaluateRequest(BaseModel):
    job_id: str