import random
import time

class MockLLMError(Exception):
    pass

class MockLLM:
    """
    Mock LLM that simulates variable response times, occasional failures (timeout/rate-limit),
    and temperature-driven randomness.
    """
    def __init__(self, failure_rate=0.12, avg_latency=0.6, seed=None):
        self.failure_rate = failure_rate
        self.avg_latency = avg_latency
        if seed is not None:
            random.seed(seed)

    def _maybe_fail(self):
        r = random.random()
        if r < self.failure_rate:
            # simulate different failure types
            if r < self.failure_rate / 2:
                raise MockLLMError("timeout")
            else:
                raise MockLLMError("rate_limit")

    def call(self, prompt: str, temperature: float = 0.2):
        # simulate latency
        latency = max(0.1, random.gauss(self.avg_latency, 0.2))
        time.sleep(latency)
        # simulate failure
        self._maybe_fail()
        # produce deterministic-ish output influenced by temperature
        base = 0.5  # base match
        # craft a fake textual response
        if "extract" in prompt.lower():
            # return simple json-like extraction
            skills = []
            for kw in ["python","django","fastapi","aws","openai","mongodb","postgres"]:
                if kw in prompt.lower():
                    skills.append(kw)
            years = 2
            return {"skills": skills, "years_experience": years, "projects": ["sample project extracted"]}
        if "score" in prompt.lower():
            # produce scores influenced by temperature
            def s():
                noise = (random.random() - 0.5) * temperature * 2  # range depends on temp
                return max(1.0, min(5.0, 3.5 + noise))
            # return scoring dictionary
            return {
                "technical_skills": round(s(),2),
                "experience": round(s(),2),
                "achievements": round(s(),2),
                "culture": round(s(),2),
                # project side
                "correctness": round(s(),2),
                "code_quality": round(s(),2),
                "resilience": round(s(),2),
                "documentation": round(s(),2),
                "creativity": round(s(),2)
            }
        # fallback summary
        strength_phrases = ["Strong backend fundamentals", "Good cloud exposure", "Limited LLM experience"]
        weakness_phrases = ["Needs stronger testing", "Improve error handling"]
        # pick based on random influenced by temperature
        pick = random.choice(strength_phrases)
        pick2 = random.choice(weakness_phrases)
        summary = f"{pick}. {pick2}."
        return {"summary": summary}
        return {"summary": "Candidate shows potential."} 