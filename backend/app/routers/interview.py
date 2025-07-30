from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.services.interview_service import InterviewService
from app.services.auth_service import get_current_user
from typing import Optional
import io

router = APIRouter(prefix="/interview", tags=["interview"])

@router.get("/test")
async def test_interview_endpoint():
    """
    Endpoint de test pour vérifier que le router fonctionne.
    """
    return JSONResponse(content={"message": "Interview router is working!"}, status_code=200)

@router.post("/generate-questions")
async def generate_interview_questions(
    cv_file: UploadFile = File(...),
    job_text: str = Form(...),
    num_questions: Optional[int] = 10
):
    """
    Génère des questions d'entretien basées sur le CV et l'offre d'emploi.
    """
    try:
        # Vérifier les types de fichiers
        if not cv_file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Le CV doit être au format PDF ou TXT")
        
        # Lire les fichiers
        cv_content = await cv_file.read()
        job_content = job_text
        
        # Générer les questions
        interview_service = InterviewService()
        result = await interview_service.generate_interview_questions(
            cv_content, 
            job_content, 
            num_questions
        )
        
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des questions: {str(e)}")

@router.post("/analyze-responses")
async def analyze_interview_responses(
    questions: list,
    answers: list,
    cv_text: str = Form(...),
    job_text: str = Form(...)
):
    """
    Analyse les réponses d'entretien et génère des suggestions personnalisées.
    """
    try:
        interview_service = InterviewService()
        result = await interview_service.analyze_responses(
            questions, 
            answers, 
            cv_text, 
            job_text
        )
        
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des réponses: {str(e)}")