import io
import zipfile

import PyPDF2
import pdfplumber
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from fastapi import UploadFile

from app.config import settings
from app.i18n import DEFAULT_LOCALE, ApiError, t
from app.models.upload import PDFUploadResponse

UNREADABLE_PDF_MESSAGE = t("upload.pdf_unreadable")
NO_TEXT_PDF_MESSAGE = t("upload.pdf_no_text")
UPLOAD_CHUNK_SIZE = 1024 * 1024

CV_EXTENSIONS = (".pdf", ".docx", ".txt")
# Au-delà, l'archive DOCX est suspecte (zip bomb) : un CV décompressé pèse quelques Mo au plus
MAX_DOCX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024
DOCX_MAIN_PART = "word/document.xml"


class ExtractionError(Exception):
    """Le fichier n'a pas pu être converti en texte ; `code` est la clé i18n du message."""

    def __init__(self, code: str):
        super().__init__(t(code))
        self.code = code


class PDFExtractionError(ExtractionError):
    """Le PDF n'a pu être lu ni par pdfplumber ni par PyPDF2."""

    def __init__(self):
        super().__init__("upload.pdf_unreadable")


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


def cv_extension(filename: str | None) -> str:
    """Extension (.pdf, .docx, .txt) d'un CV accepté ; 400 pour tout autre format."""
    name = (filename or "").lower()
    for extension in CV_EXTENSIONS:
        if name.endswith(extension):
            return extension
    raise ApiError(400, "upload.cv_format")


def _is_pdf(content: bytes) -> bool:
    # La spécification tolère des octets parasites avant l'en-tête, dans le premier Ko
    return b"%PDF-" in content[:1024]


def _is_zip(content: bytes) -> bool:
    return content.startswith(b"PK\x03\x04")


def _check_signature(extension: str, content: bytes) -> None:
    """Le contenu doit correspondre à l'extension : on ne se fie ni au nom ni au MIME envoyés."""
    if extension == ".pdf":
        valid = _is_pdf(content)
    elif extension == ".docx":
        valid = _is_zip(content)
    else:
        # Un .txt ne contient pas d'octet nul (binaire, UTF-16…) ni la signature d'un autre format
        valid = b"\x00" not in content and not _is_pdf(content) and not _is_zip(content)
    if not valid:
        raise ExtractionError("upload.signature_mismatch")


def _docx_blocks(document):
    """Paragraphes et tableaux du corps, dans l'ordre du document."""
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


def _docx_paragraph_text(paragraph: Paragraph) -> str:
    text = paragraph.text.strip()
    p_pr = paragraph._p.pPr
    is_list_item = (p_pr is not None and p_pr.numPr is not None) or (
        paragraph.style is not None and paragraph.style.name.startswith("List")
    )
    return f"- {text}" if text and is_list_item else text


def _docx_table_lines(table: Table) -> list[str]:
    lines = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            # Les cellules fusionnées sont renvoyées plusieurs fois par python-docx
            text = cell.text.strip()
            if text and (not cells or cells[-1] != text):
                cells.append(text)
        if cells:
            lines.append(" | ".join(cells))
    return lines


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
            raise PDFExtractionError() from e

    def extract_text_from_docx(self, content: bytes) -> str:
        """Extrait le texte d'un DOCX : paragraphes, listes (préfixées « - ») et tableaux."""
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                infos = archive.infolist()
                names = {info.filename for info in infos}
                if sum(info.file_size for info in infos) > MAX_DOCX_UNCOMPRESSED_SIZE:
                    raise ExtractionError("upload.docx_unreadable")
            if DOCX_MAIN_PART not in names:
                # Archive ZIP qui n'est pas un document Word (.xlsx, .zip renommé…)
                raise ExtractionError("upload.signature_mismatch")
            document = Document(io.BytesIO(content))
            lines = []
            for block in _docx_blocks(document):
                if isinstance(block, Paragraph):
                    lines.append(_docx_paragraph_text(block))
                else:
                    lines.extend(_docx_table_lines(block))
        except ExtractionError:
            raise
        except Exception as e:
            print(f"python-docx failed: {e}")
            raise ExtractionError("upload.docx_unreadable") from e
        return "\n".join(line for line in lines if line).strip()

    def extract_cv_text(self, filename: str, content: bytes) -> str:
        """Texte d'un CV PDF, DOCX ou TXT (UTF-8, sinon Latin-1), après contrôle de la signature."""
        extension = cv_extension(filename)
        _check_signature(extension, content)
        if extension == ".pdf":
            return self.extract_text_from_bytes(content)
        if extension == ".docx":
            return self.extract_text_from_docx(content)
        try:
            return content.decode("utf-8").strip()
        except UnicodeDecodeError:
            return content.decode("latin-1").strip()

    async def extract_upload(self, file: UploadFile) -> str:
        """Lit et extrait un CV importé : format (400), taille (413), contenu (ExtractionError)."""
        extension = cv_extension(file.filename)
        content = await read_upload(file)
        text = self.extract_cv_text(file.filename, content)
        if not text:
            raise ExtractionError("upload.pdf_no_text" if extension == ".pdf" else "upload.empty_file")
        return text

    async def extract_upload_or_400(self, file: UploadFile) -> str:
        """`extract_upload` pour les routes qui répondent 400 quand le CV est illisible."""
        try:
            return await self.extract_upload(file)
        except ExtractionError as e:
            raise ApiError(400, e.code) from e

    async def pdf_upload_response(self, file: UploadFile, locale: str = DEFAULT_LOCALE) -> PDFUploadResponse:
        """Traitement commun des routes d'upload de CV (PDF, DOCX ou TXT)."""
        try:
            text = await self.extract_upload(file)
        except ExtractionError as e:
            return PDFUploadResponse(success=False, text="", message=t(e.code, locale))
        return PDFUploadResponse(
            success=True,
            text=text,
            message=t("upload.extracted", locale, count=len(text)),
        )
