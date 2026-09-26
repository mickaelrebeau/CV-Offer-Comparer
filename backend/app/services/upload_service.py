import io

import PyPDF2
import pdfplumber
from fastapi import UploadFile

from app.config import settings
from app.i18n import DEFAULT_LOCALE, ApiError, t
from app.models.upload import PDFUploadResponse

UNREADABLE_PDF_MESSAGE = t("upload.pdf_unreadable")
NO_TEXT_PDF_MESSAGE = t("upload.pdf_no_text")
UPLOAD_CHUNK_SIZE = 1024 * 1024


class PDFExtractionError(Exception):
    """Le PDF n'a pu être lu ni par pdfplumber ni par PyPDF2."""


async def read_upload(file: UploadFile, max_size: int | None = None) -> bytes:
    """Lit un upload par blocs en refusant (413) tout fichier au-delà de MAX_FILE_SIZE."""
    limit = max_size or settings.MAX_FILE_SIZE
    too_large = ApiError(413, "upload.too_large", max_mb=limit // (1024 * 1024))
    if file.size is not None and file.size > limit:
        raise too_large
    content = bytearray()
    while chunk := await file.read(UPLOAD_CHUNK_SIZE):
        content.extend(chunk)
        if len(content) > limit:
            raise too_large
    return bytes(content)


class UploadService:
    def extract_text_from_bytes(self, content: bytes) -> str:
        """Extrait le texte d'un PDF (pdfplumber, puis PyPDF2 en secours)."""
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages).strip()
        except Exception as e:
            print(f"pdfplumber failed: {e}")

        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages).strip()
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            raise PDFExtractionError(UNREADABLE_PDF_MESSAGE) from e

    def extract_cv_text(self, filename: str, content: bytes) -> str:
        """Texte d'un CV PDF ou TXT (UTF-8, sinon Latin-1)."""
        if filename.lower().endswith(".pdf"):
            return self.extract_text_from_bytes(content)
        try:
            return content.decode("utf-8").strip()
        except UnicodeDecodeError:
            return content.decode("latin-1").strip()

    async def pdf_upload_response(self, file: UploadFile, locale: str = DEFAULT_LOCALE) -> PDFUploadResponse:
        """Traitement commun des routes d'upload de CV PDF."""
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise ApiError(400, "upload.only_pdf")

        content = await read_upload(file)
        try:
            text = self.extract_text_from_bytes(content)
        except PDFExtractionError:
            return PDFUploadResponse(success=False, text="", message=t("upload.pdf_unreadable", locale))

        if not text:
            return PDFUploadResponse(success=False, text="", message=t("upload.pdf_no_text", locale))
        return PDFUploadResponse(
            success=True,
            text=text,
            message=t("upload.extracted", locale, count=len(text)),
        )
