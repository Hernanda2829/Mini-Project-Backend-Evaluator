import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routes import router

# Load environment variables dari .env
load_dotenv()
print("API KEY:", os.getenv("OPENROUTER_API_KEY"))


def create_app():
    app = FastAPI(
        title="Mini Project - Backend Evaluator",
        version="1.0.0",
        description="API untuk upload CV, evaluasi dengan LLM, dan ambil hasil"
    )

    # register router
    app.include_router(router)

    # endpoint root untuk test server
    @app.get("/")
    def root():
        return {"message": "server jalan"}

    return app


app = create_app()

# pastikan folder ada
os.makedirs("uploads", exist_ok=True)
os.makedirs("data/submissions", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)