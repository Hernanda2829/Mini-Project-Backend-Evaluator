from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np

class SimpleRAG:
    """
    Simple RAG using TF-IDF over provided documents (job description + rubric).
    Not a production vector DB but meets the 'vector retrieval' behavior for the task.
    """
    def __init__(self, doc_paths):
        self.doc_texts = []
        self.doc_names = []
        for p in doc_paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
                # split into paragraphs for finer retrieval
                paras = [para.strip() for para in txt.split("\n\n") if para.strip()]
                for i, para in enumerate(paras):
                    self.doc_texts.append(para)
                    self.doc_names.append(f"{os.path.basename(p)}::para_{i}")
        if not self.doc_texts:
            # fallback: add a short default doc
            self.doc_texts = ["Backend role: backend, databases, APIs, cloud, LLM exposure. Scoring rubric included."]
            self.doc_names = ["default"]
        self.vectorizer = TfidfVectorizer().fit(self.doc_texts)
        self.doc_vectors = self.vectorizer.transform(self.doc_texts)

    def retrieve(self, query: str, top_k: int = 3):
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.doc_vectors)[0]
        idx = np.argsort(-sims)[:top_k]
        results = [{"name": self.doc_names[i], "text": self.doc_texts[i], "score": float(sims[i])} for i in idx]
        return results
