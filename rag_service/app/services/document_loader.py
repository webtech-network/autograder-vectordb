import io
from pathlib import Path

from pypdf import PdfReader


class DocumentLoaderService:
    @staticmethod
    def extract_text(filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            return DocumentLoaderService._extract_pdf_text(content)
        return content.decode("utf-8", errors="ignore")

    @staticmethod
    def _extract_pdf_text(content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
