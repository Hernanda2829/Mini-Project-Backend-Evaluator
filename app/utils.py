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