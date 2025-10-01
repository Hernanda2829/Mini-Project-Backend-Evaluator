<<<<<<< HEAD
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

        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        output = resp.json()

        if "choices" not in output:
            return {"error": "Unexpected response format", "details": output}

        result_text = output["choices"][0]["message"]["content"]
        return {"feedback": result_text}
        
=======
from app.utils import extract_text_generic, simple_cv_parser
from app.rag import SimpleRAG
from app.mock_llm import MockLLM, MockLLMError
from app.storage import JobStorage
import time
import math

# weights from PDF rubrics
CV_WEIGHTS = {
    "technical_skills": 0.40,
    "experience": 0.25,
    "achievements": 0.20,
    "culture": 0.15
}
PROJECT_WEIGHTS = {
    "correctness": 0.30,
    "code_quality": 0.25,
    "resilience": 0.20,
    "documentation": 0.15,
    "creativity": 0.10
}

class Evaluator:
    def __init__(self, job_description_path="data/job_description.txt", rubric_path="data/scoring_rubric.txt"):
        self.rag = SimpleRAG([job_description_path, rubric_path])
        # mock LLM with some failure rate
        self.llm = MockLLM(failure_rate=0.12, avg_latency=0.4)
        self.storage = JobStorage()

    def _retrieve_context(self, purpose: str, text: str):
        q = f"{purpose}: {text[:800]}"
        return self.rag.retrieve(q, top_k=3)

    def _call_llm_with_retries(self, prompt, temperature=0.2, retries=3, backoff_base=0.5):
        attempt = 0
        while True:
            try:
                resp = self.llm.call(prompt, temperature=temperature)
                return resp
            except MockLLMError as e:
                attempt += 1
                if attempt > retries:
                    # final fallback: deterministic conservative output
                    # For scoring: return neutral medium scores
                    return {"fallback": True}
                wait = backoff_base * (2 ** (attempt-1))
                time.sleep(wait)

    def score_cv(self, cv_text: str, temperature=0.2):
        # Step: retrieval
        contexts = self._retrieve_context("cv_scoring", cv_text)
        prompt = "Extract and score: " + cv_text[:1500] + "\n\nCONTEXT:\n" + "\n".join([c["text"] for c in contexts])
        llm_resp = self._call_llm_with_retries(prompt, temperature=temperature)
        if isinstance(llm_resp, dict) and llm_resp.get("fallback"):
            # fallback deterministic scoring based on simple heuristics
            parsed = simple_cv_parser(cv_text)
            skills = len(parsed["skills"])
            years = parsed["years_experience"]
            # map to 1-5
            technical = min(5, 1 + skills // 2)
            experience = min(5, 1 + years // 2)
            achievements = 2
            culture = 3
            scores = {
                "technical_skills": technical,
                "experience": experience,
                "achievements": achievements,
                "culture": culture
            }
        else:
            # if mock returns scoring dict
            if all(k in llm_resp for k in ["technical_skills","experience"]):
                scores = {k: float(v) for k,v in llm_resp.items() if k in CV_WEIGHTS}
            else:
                # fallback to parser as above
                parsed = simple_cv_parser(cv_text)
                skills = len(parsed["skills"])
                years = parsed["years_experience"]
                technical = min(5, 1 + skills // 2)
                experience = min(5, 1 + years // 2)
                achievements = 2
                culture = 3
                scores = {
                    "technical_skills": technical,
                    "experience": experience,
                    "achievements": achievements,
                    "culture": culture
                }
        # weighted aggregate to percentage (1-5 -> 20%-100%)
        weighted = 0.0
        for k,w in CV_WEIGHTS.items():
            weighted += scores.get(k,3) * w
        match_rate = round((weighted / 5.0), 4)  # between 0.2 and 1.0
        # textual feedback (use llm for text if possible)
        feedback_prompt = f"Generate CV feedback. Scores: {scores}. Contexts: {contexts}"
        feedback_resp = self._call_llm_with_retries(feedback_prompt, temperature=temperature)
        if isinstance(feedback_resp, dict) and "summary" in feedback_resp:
            cv_feedback = feedback_resp["summary"]
        else:
            # simple feedback
            cv_feedback = f"Technical skills: {scores['technical_skills']}/5. Experience: {scores['experience']}/5. Achievements: {scores['achievements']}/5. Culture: {scores['culture']}/5."

        return {"scores": scores, "match_rate": match_rate, "feedback": cv_feedback}

    def score_project(self, report_text: str, temperature=0.2):
        contexts = self._retrieve_context("project_scoring", report_text)
        prompt = "Score project: " + report_text[:1500] + "\n\nCONTEXT:\n" + "\n".join([c["text"] for c in contexts])
        llm_resp = self._call_llm_with_retries(prompt, temperature=temperature)
        if isinstance(llm_resp, dict) and llm_resp.get("fallback"):
            # heuristic fallback
            scores = {
                "correctness": 3,
                "code_quality": 3,
                "resilience": 2,
                "documentation": 3,
                "creativity": 2
            }
        else:
            keys = ["correctness","code_quality","resilience","documentation","creativity"]
            if all(k in llm_resp for k in keys):
                scores = {k: float(llm_resp[k]) for k in keys}
            else:
                # try pick values
                scores = {k: float(llm_resp.get(k, 3.0)) for k in keys}
        # aggregate to 1-10 scale project score
        weighted = 0.0
        for k,w in PROJECT_WEIGHTS.items():
            weighted += scores.get(k,3) * w
        # map 1-5 to 0-10: (weighted/5)*10
        project_score = round((weighted / 5.0) * 10, 2)
        # feedback
        feedback_prompt = f"Generate project feedback. Scores: {scores}. Contexts: {contexts}"
        feedback_resp = self._call_llm_with_retries(feedback_prompt, temperature=temperature)
        if isinstance(feedback_resp, dict) and "summary" in feedback_resp:
            project_feedback = feedback_resp["summary"]
        else:
            project_feedback = f"Project scored {project_score}/10. Details: {scores}"

        return {"scores": scores, "project_score": project_score, "feedback": project_feedback}

    def evaluate_job(self, job):
        # job contains cv_path and report_path
        cv_text = extract_text_generic(job["cv_path"])
        report_text = extract_text_generic(job["report_path"])
        # update status externally by caller
        # use temperature saved per job if desired; default 0.2
        temperature = 0.2
        cv_result = self.score_cv(cv_text, temperature=temperature)
        proj_result = self.score_project(report_text, temperature=temperature)
        # overall summary
        cv_percent = int(round(cv_result["match_rate"] * 100))
        overall_summary = f"CV match rate {cv_percent}%. Project score {proj_result['project_score']}/10. {cv_result['feedback']} {proj_result['feedback']}"
        result = {
            "cv_match_rate": cv_result["match_rate"],
            "cv_feedback": cv_result["feedback"],
            "project_score": proj_result["project_score"],
            "project_feedback": proj_result["feedback"],
            "overall_summary": overall_summary
        }
        return result
>>>>>>> 59a67804aec833ff347d39cfbdf8cc78a0077eb0
