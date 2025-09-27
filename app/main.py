from fastapi import FastAPI
from app.routes import router
import os

def create_app():
    app = FastAPI(title="Mini Project - Backend Evaluator")
    app.include_router(router)
    return app

app = create_app()

# ensure uploads and data folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("data/submissions", exist_ok=True)