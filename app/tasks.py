import os
import threading
from app.evaluator import Evaluator
from app.job_storage import JobStorage
from app.utils import extract_text_generic

job_storage = JobStorage()
evaluator = Evaluator()

def start_evaluation_job(job_id: str):
    def run():
        job = job_storage.get_job(job_id)
        if not job:
            return

        try:
            # update status ke "running"
            job_storage.update_status(job_id, "running")

            # ambil teks dari CV
            cv_text = extract_text_generic(job["cv_path"])
            print("\n===== DEBUG CV TEXT (awal 500 chars) =====")
            print(cv_text[:500])
            print("==========================================\n")

            if not cv_text or cv_text.startswith("[Error"):
                result = {"error": f"Gagal membaca CV: {cv_text}"}
            else:
                # evaluasi pakai LLM
                result = evaluator.evaluate(cv_text)

            # simpan hasil ke DB
            job_storage.write_result(job_id, result)

        except Exception as e:
            job_storage.write_result(job_id, {"error": str(e)})

    # jalanin di thread biar async
    threading.Thread(target=run).start()