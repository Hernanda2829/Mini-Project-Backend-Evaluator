from app.storage import JobStorage
from app.evaluator import Evaluator
import time
import traceback

storage = JobStorage()
evaluator = Evaluator()

def start_evaluation_job(job_id: str, temperature: float = 0.2):
    """
    This function is intended to be run in background (FastAPI BackgroundTasks).
    It simulates async long-running task with status updates.
    """
    try:
        storage.update_status(job_id, "processing")
        job = storage.get_job(job_id)
        # small delay to simulate queue start
        time.sleep(0.5)
        # call evaluator
        result = evaluator.evaluate_job(job)
        # write result
        storage.write_result(job_id, result)
    except Exception as e:
        # on failure, store error in result
        tb = traceback.format_exc()
        storage.write_result(job_id, {"error": str(e), "trace": tb})
        storage.update_status(job_id, "failed")