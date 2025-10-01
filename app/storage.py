import sqlite3
import json
import time
from typing import Optional

class JobStorage:
    def __init__(self, db_path="jobs.db"):
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        conn = self._conn()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                cv_path TEXT,
                report_path TEXT,
                status TEXT,
                created_at INTEGER,
                updated_at INTEGER,
                result TEXT
            )
        """)
        conn.commit()
        conn.close()

    def create_job(self, cv_path: str, report_path: str) -> str:
        import uuid, time
        job_id = str(uuid.uuid4())
        now = int(time.time())
        conn = self._conn()
        c = conn.cursor()
        c.execute("INSERT INTO jobs (id, cv_path, report_path, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (job_id, cv_path, report_path, "created", now, now))
        conn.commit()
        conn.close()
        return job_id

    def get_job(self, job_id: str) -> Optional[dict]:
        conn = self._conn()
        c = conn.cursor()
        c.execute("SELECT id, cv_path, report_path, status, created_at, updated_at, result FROM jobs WHERE id = ?", (job_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return None
        res = {
            "id": row[0],
            "cv_path": row[1],
            "report_path": row[2],
            "status": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "result": json.loads(row[6]) if row[6] else None
        }
        return res

    def update_status(self, job_id: str, status: str):
        import time
        now = int(time.time())
        conn = self._conn()
        c = conn.cursor()
        c.execute("UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?", (status, now, job_id))
        conn.commit()
        conn.close()

    def write_result(self, job_id: str, result: dict):
        import time, json
        now = int(time.time())
        conn = self._conn()
        c = conn.cursor()
        c.execute("UPDATE jobs SET result = ?, status = ?, updated_at = ? WHERE id = ?",
                  (json.dumps(result), "completed", now, job_id))
        conn.commit()
        conn.close()
