<<<<<<< HEAD
# Mini-Project-Backend-Evaluator
=======
# Mini Project - Backend Evaluator (FastAPI)

This project implements a backend service for evaluating candidate CV + project report against a job description and scoring rubric. It is a self-contained prototype that demonstrates:

- File upload (CV + project report)
- Async evaluation pipeline with job queue semantics (queued -> processing -> completed)
- Simple RAG retrieval (TF-IDF based)
- Mock LLM with failure simulation + retry/backoff + temperature control
- Scoring & feedback generation
- SQLite-based job storage

## Quickstart (local)

1. Create virtual environment and install deps:
```bash
python -m venv .venv
source .venv/bin/activate   # on Windows use .venv\\Scripts\\activate
pip install -r requirements.txt
>>>>>>> 59a6780 (feat: Implement backend evaluator service with FastAPI)
