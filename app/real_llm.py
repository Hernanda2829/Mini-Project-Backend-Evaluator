import os
import requests
from dotenv import load_dotenv

load_dotenv()  # ini akan baca file .env

class RealLLM:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def call(self, prompt: str, temperature: float = 0.2):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "mistralai/mistral-7b-instruct",  # contoh model gratis
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        resp = requests.post(self.base_url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
