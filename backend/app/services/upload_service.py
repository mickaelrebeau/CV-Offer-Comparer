import io

import PyPDF2
import pdfplumber
from fastapi import HTTPException, UploadFile

from app.config import settings
from app.models.upload import PDFUploadResponse

UNREADABLE_PDF_MESSAGE = (
    "PDF illisible ou corrompu. Réexportez votre CV en PDF, ou collez son texte directement."
)
NO_TEXT_PDF_MESSAGE = (
    "Ce PDF ne contient pas de texte lisible (PDF scanné ou image ?). "
    "Exportez votre CV en PDF texte, ou collez son texte directement."
)
UPLOAD_CHUNK_SIZE = 1024 * 1024


class PDFExtractionError(Exception):
    """Le PDF n'a pu être lu ni par pdfplumber ni par PyPDF2."""


async def read_upload(file: UploadFile, max_size: int | None = None) -> bytes:
    """Lit un upload par blocs en refusant (413) tout fichier au-delà de MAX_FILE_SIZE."""
    limit = max_size or settings.MAX_FILE_SIZE
    too_large = HTTPException(
        status_code=413,
        detail=f"Le fichier est trop volumineux (max {limit // (1024 * 1024)} Mo)",
    )
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

    async def pdf_upload_response(self, file: UploadFile) -> PDFUploadResponse:
        """Traitement commun des routes d'upload de CV PDF."""
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")

        content = await read_upload(file)
        try:
            text = self.extract_text_from_bytes(content)
        except PDFExtractionError as e:
            return PDFUploadResponse(success=False, text="", message=str(e))

        if not text:
            return PDFUploadResponse(success=False, text="", message=NO_TEXT_PDF_MESSAGE)
        return PDFUploadResponse(
            success=True,
            text=text,
            message=f"Texte extrait avec succès ({len(text)} caractères)",
        )
