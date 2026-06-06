import os
import whisper
import PyPDF2
import docx
from pathlib import Path


# Load Whisper model once at startup — not on every request
# "base" is fast enough for portfolio, accurate enough for demos
# Downloads ~150MB on first run, cached after that
whisper_model = whisper.load_model("base")


def parse_input(file_path: str = None, text: str = None) -> str:
    """
    Master function — accepts ANY input, always returns plain text.
    
    Priority order:
    1. If text is passed directly → return it as is
    2. If file is passed → detect type → extract text
    """

    # ── Direct text input (pasted transcript) ─────────────────────────────────
    if text and text.strip():
        return text.strip()

    # ── File input ─────────────────────────────────────────────────────────────
    if not file_path:
        raise ValueError("Either file_path or text must be provided")

    ext = Path(file_path).suffix.lower()

    # ── Audio files → Whisper ──────────────────────────────────────────────────
    if ext in [".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".webm"]:
        return _parse_audio(file_path)

    # ── PDF ────────────────────────────────────────────────────────────────────
    elif ext == ".pdf":
        return _parse_pdf(file_path)

    # ── Word document ──────────────────────────────────────────────────────────
    elif ext == ".docx":
        return _parse_docx(file_path)

    # ── Plain text ─────────────────────────────────────────────────────────────
    elif ext == ".txt":
        return _parse_txt(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: mp3, mp4, wav, m4a, ogg, webm, pdf, docx, txt")


def _parse_audio(file_path: str) -> str:
    """Audio → text via Whisper"""
    result = whisper_model.transcribe(file_path)
    return result["text"].strip()


def _parse_pdf(file_path: str) -> str:
    """PDF → text via PyPDF2"""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()


def _parse_docx(file_path: str) -> str:
    """Word doc → text via python-docx"""
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    return text.strip()


def _parse_txt(file_path: str) -> str:
    """Plain text file → text"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()
