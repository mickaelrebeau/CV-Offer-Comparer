import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.interview_record import InterviewRecord
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["interview"])


@router.get("/test")
async def test_interview_endpoint():
    """Endpoint de test pour vérifier que le router fonctionne."""
    return JSONResponse(content={"message": "Interview router is working!"}, status_code=200)


@router.post("/generate-questions")
async def generate_interview_questions(
    cv_file: UploadFile = File(...),
    job_text: str = Form(...),
    num_questions: Optional[int] = Form(default=10),
    user: User = Depends(get_current_user),
):
    """Génère des questions d'entretien basées sur le CV et l'offre d'emploi."""
    try:
        if not cv_file.filename or not cv_file.filename.lower().endswith((".pdf", ".txt")):
            raise HTTPException(status_code=400, detail="Le CV doit être au format PDF ou TXT")

        cv_content = await cv_file.read()
        interview_service = InterviewService()
        result = await interview_service.generate_interview_questions(
            cv_content,
            job_text,
            num_questions or 10,
        )

        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des questions: {str(e)}",
        ) from e


@router.post("/analyze-responses")
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

        interview_service = InterviewService()
        result = await interview_service.analyze_responses(
            questions_list,
            answers_list,
            cv_text,
            job_text,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

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
        raise HTTPException(status_code=400, detail=f"Format JSON invalide: {str(e)}") from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse des réponses: {str(e)}",
        ) from e
