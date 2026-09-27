import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import require_debug_endpoints
from app.i18n import ApiError, request_locale, t
from app.models.interview_record import InterviewRecord
from app.models.user import User
from app.services.auth_service import get_current_user, require_verified_user
from app.services.interview_service import InterviewService
from app.services.llm_credentials_service import ai_for_user
from app.services.upload_service import PDFExtractionError, UploadService, read_upload
from app.services.rate_limit_service import rate_limit

router = APIRouter(prefix="/interview", tags=["interview"])
upload_service = UploadService()


@router.get("/test", dependencies=[Depends(require_debug_endpoints)], include_in_schema=False)
async def test_interview_endpoint():
    """Endpoint de test pour vérifier que le router fonctionne."""
    return JSONResponse(content={"message": "Interview router is working!"}, status_code=200)


@router.post(
    "/generate-questions",
    dependencies=[
        Depends(require_verified_user),
        Depends(rate_limit("interview_generate", "DAILY_QUOTA_INTERVIEW_GENERATE")),
    ],
)
async def generate_interview_questions(
    cv_file: UploadFile = File(...),
    job_text: str = Form(...),
    num_questions: Optional[int] = Form(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    """Génère des questions d'entretien basées sur le CV et l'offre d'emploi."""
    try:
        if not cv_file.filename or not cv_file.filename.lower().endswith((".pdf", ".txt")):
            raise ApiError(400, "upload.cv_format")

        cv_content = await read_upload(cv_file)
        try:
            cv_text = upload_service.extract_cv_text(cv_file.filename, cv_content)
        except PDFExtractionError as e:
            raise ApiError(400, "upload.pdf_unreadable") from e
        if not cv_text:
            is_pdf = cv_file.filename.lower().endswith(".pdf")
            raise ApiError(400, "upload.pdf_no_text" if is_pdf else "upload.empty_file")

        interview_service = InterviewService(ai_for_user(db, user))
        result = await interview_service.generate_interview_questions(
            cv_text,
            job_text,
            num_questions or 10,
        )

        if result["success"]:
            count = len(result["interview_session"]["questions"])
            content = {**result, "message": t("interview.questions_generated", locale, count=count)}
            return JSONResponse(content=content, status_code=200)
        code = result.get("code", "interview.questions_failed")
        raise ApiError(400 if code in ("interview.job_empty", "upload.empty_file") else 500, code)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Interview] generate-questions: {e!r}")
        raise ApiError(500, "interview.questions_failed") from e


@router.post(
    "/analyze-responses",
    dependencies=[
        Depends(require_verified_user),
        Depends(rate_limit("interview_analyze", "DAILY_QUOTA_INTERVIEW_ANALYZE")),
    ],
)
async def analyze_interview_responses(
    questions: str = Form(...),
    answers: str = Form(...),
    cv_text: str = Form(...),
    job_text: str = Form(...),
    duration_seconds: int = Form(default=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyse les réponses d'entretien, génère des suggestions et enregistre l'historique."""
    try:
        questions_list = json.loads(questions)
        answers_list = json.loads(answers)

        interview_service = InterviewService(ai_for_user(db, user))
        result = await interview_service.analyze_responses(
            questions_list,
            answers_list,
            cv_text,
            job_text,
        )

        if not result["success"]:
            raise ApiError(500, result.get("code", "interview.analysis_failed"))

        analysis = result.get("analysis") or {}
        record = InterviewRecord.from_session(
            user_id=user.id,
            job_text=job_text,
            cv_text=cv_text,
            questions=questions_list,
            answers=answers_list,
            analysis=analysis,
            duration_seconds=duration_seconds,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return JSONResponse(
            content={
                **result,
                "interview_id": str(record.id),
            },
            status_code=200,
        )

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise ApiError(400, "interview.invalid_payload") from e
    except Exception as e:
        print(f"[Interview] analyze-responses: {e!r}")
        raise ApiError(500, "interview.analysis_failed") from e
