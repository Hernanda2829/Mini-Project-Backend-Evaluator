<<<<<<< HEAD
import pdfplumber
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image

def extract_text_generic(file_path: str) -> str:
    """
    Ekstraksi teks dari PDF.
    - Jika bisa: langsung pakai pdfplumber
    - Jika gagal (PDF hasil scan / gambar): fallback ke OCR
    """
    text = ""

    try:
        if file_path.lower().endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # coba ambil teks langsung
                    page_text = page.extract_text()

                    if not page_text:
                        # fallback: OCR
                        pil_img = page.to_image(resolution=300).original
                        page_text = pytesseract.image_to_string(pil_img, lang="eng")

                    text += (page_text or "") + "\n"
        else:
            return f"[Error] Unsupported file type: {file_path}"

        text = text.strip()
        if not text:
            return "[Error] Tidak berhasil mengekstrak teks dari CV"

        return text

    except Exception as e:
        return f"[Error] Exception saat ekstrak: {str(e)}"
=======
from typing import List
import re
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(path: str) -> str:
    try:
        reader = PdfReader(path)
        texts = []
        for p in reader.pages:
            texts.append(p.extract_text() or "")
        return "\n".join(texts)
    except Exception:
        return ""

def extract_text_from_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""

def extract_text_generic(path: str) -> str:
    path = path.lower()
    if path.endswith(".pdf"):
        return extract_text_from_pdf(path)
    if path.endswith(".docx"):
        return extract_text_from_docx(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def simple_cv_parser(text: str) -> dict:
    """
    Very simple CV extractor: looks for keywords and years.
    Returns structured dict: skills list, experiences (years), projects summary.
    """
    skills = []
    # common keywords
    keywords = ["python", "node", "django", "flask", "fastapi", "sql", "postgres", "mysql", "mongodb",
                "aws", "gcp", "azure", "docker", "kubernetes", "llm", "openai", "embeddings", "faiss",
                "rest", "api", "graphql", "ci/cd", "testing", "pytest"]
    text_low = text.lower()
    for kw in keywords:
        if kw in text_low:
            skills.append(kw)
    # extract simple year-based experience: count years mentioned like "2019-2022" or "3 years"
    years = 0
    import re
    m = re.search(r"(\d+)\s+years", text_low)
    if m:
        years = int(m.group(1))
    else:
        # try date range
        m2 = re.findall(r"(20\d{2})", text_low)
        if m2 and len(m2) >= 2:
            years = abs(int(m2[-1]) - int(m2[0]))
    projects = []
    # naive: split by "project" words
    for part in text.split("\n\n"):
        if "project" in part.lower():
            projects.append(part.strip()[:800])
    return {"skills": list(set(skills)), "years_experience": years, "projects": projects}
>>>>>>> 59a67804aec833ff347d39cfbdf8cc78a0077eb0
