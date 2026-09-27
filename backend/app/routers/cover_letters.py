from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import ApiError, request_locale
from app.models.cover_letter_record import CoverLetterRecord
from app.models.user import User
from app.routers.compare import _sse_headers
from app.services.auth_service import get_current_user, require_verified_user
from app.services.cover_letter_service import LANGUAGES, LENGTHS, TONES, stream_cover_letter
from app.services.llm_credentials_service import ai_for_user
from app.services.rate_limit_service import rate_limit
from app.services.upload_service import PDFExtractionError, UploadService, read_upload

router = APIRouter(tags=["cover-letters"])
upload_service = UploadService()

# Au-delà, le texte n'est plus un CV ou une offre (et Gemini n'en lirait de toute façon qu'une partie)
MAX_TEXT_CHARS = 50_000


async def _cv_text_from(cv_file: UploadFile | None, cv_text: str | None) -> str:
    """Texte du CV : fichier PDF/TXT importé (prioritaire) ou texte collé."""
    if cv_file is not None and cv_file.filename:
        if not cv_file.filename.lower().endswith((".pdf", ".txt")):
            raise ApiError(400, "upload.cv_format")
        content = await read_upload(cv_file)
        try:
            text = upload_service.extract_cv_text(cv_file.filename, content)
        except PDFExtractionError as e:
            raise ApiError(400, "upload.pdf_unreadable") from e
        if not text:
            is_pdf = cv_file.filename.lower().endswith(".pdf")
            raise ApiError(400, "upload.pdf_no_text" if is_pdf else "upload.empty_file")
        return text
    return (cv_text or "").strip()


@router.post(
    "/cover-letter",
    dependencies=[
        Depends(require_verified_user),
        Depends(rate_limit("cover_letter", "DAILY_QUOTA_COVER_LETTER")),
    ],
)
async def generate_cover_letter(
    job_text: str = Form(default=""),
    cv_text: Optional[str] = Form(default=None),
    cv_file: Optional[UploadFile] = File(default=None),
    tone: str = Form(default="professional"),
    length: str = Form(default="standard"),
    language: str = Form(default="auto"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    """Génère une lettre de motivation (flux SSE) et l'enregistre dans l'historique."""
    if tone not in TONES or length not in LENGTHS or language not in LANGUAGES:
        raise ApiError(400, "cover_letter.invalid_option")

    job = job_text.strip()
    if not job:
        raise ApiError(400, "interview.job_empty")
    cv = await _cv_text_from(cv_file, cv_text)
    if not cv:
        raise ApiError(400, "cover_letter.cv_missing")
    if len(job) > MAX_TEXT_CHARS or len(cv) > MAX_TEXT_CHARS:
        raise ApiError(413, "cover_letter.text_too_long", max_chars=MAX_TEXT_CHARS)

    ai = ai_for_user(db, user)

    def persist(letter) -> str:
        record = CoverLetterRecord.from_generation(
            user_id=user.id,
            job_text=job,
            cv_text=cv,
            tone=tone,
            length=length,
            letter=letter,
        )
        db.add(record)
        db.commit()
        return str(record.id)

    return StreamingResponse(
        stream_cover_letter(
            cv,
            job,
            tone=tone,
            length=length,
            language=language,
            locale=locale,
            on_result=persist,
            ai=ai,
        ),
        media_type="text/event-stream",
        headers=_sse_headers(),
    )


@router.get("/cover-letters")
def list_cover_letters(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    total = db.scalar(
        select(func.count())
        .select_from(CoverLetterRecord)
        .where(CoverLetterRecord.user_id == user.id)
    ) or 0

    rows = db.scalars(
        select(CoverLetterRecord)
        .where(CoverLetterRecord.user_id == user.id)
        .order_by(CoverLetterRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": [row.to_list_dict() for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/cover-letters/{letter_id}")
def get_cover_letter(
    letter_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(CoverLetterRecord, letter_id)
    if not row or row.user_id != user.id:
        raise ApiError(404, "history.cover_letter_not_found")
    return row.to_detail_dict()


@router.delete("/cover-letters/{letter_id}")
def delete_cover_letter(
    letter_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(CoverLetterRecord, letter_id)
    if not row or row.user_id != user.id:
        raise ApiError(404, "history.cover_letter_not_found")
    db.delete(row)
    db.commit()
    return {"success": True}
