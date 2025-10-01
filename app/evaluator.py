import os
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()  # Load environment variables from .env file

class Evaluator:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Ekstrak teks dari PDF"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()

    def evaluate_text(self, cv_text: str) -> dict:
        MAX_CHARS = 4000
        if len(cv_text) > MAX_CHARS:
            cv_text = cv_text[:MAX_CHARS] + "\n\n[Truncated due to length]"

        prompt = f"""
Berikut adalah CV kandidat (dipotong bila terlalu panjang):

{cv_text}

Tolong evaluasi CV ini secara singkat:
- Kelebihan
- Kekurangan
- Rekomendasi perbaikan
- Skor (1-10)
"""

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)  # ⬅️ timeout 30 detik
            resp.raise_for_status()
            output = resp.json()

            if "choices" not in output:
                return {"error": "Unexpected response format", "details": output}

            result_text = output["choices"][0]["message"]["content"]
            return {"feedback": result_text}

        except requests.exceptions.Timeout:
            return {"error": "Request ke OpenRouter timeout, coba lagi."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Gagal request ke OpenRouter: {str(e)}"}
