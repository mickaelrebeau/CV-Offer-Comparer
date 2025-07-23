from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.upload import PDFUploadResponse
from app.services.upload_service import UploadService
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()
upload_service = UploadService()

@router.post("/upload-cv", response_model=PDFUploadResponse)
async def upload_cv_pdf(
    file: UploadFile = File(...),
    user=Depends(auth_service.verify_token)
):
    """Upload et extraction de texte d'un CV PDF"""
    
    # Vérifier le type de fichier
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    # Vérifier la taille du fichier
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (max 10MB)")
    
    try:
        # Extraire le texte du PDF
        extracted_text = upload_service.extract_text_from_pdf(file)
        
        if not extracted_text.strip():
            return PDFUploadResponse(
                success=False,
                text="",
                message="Aucun texte n'a pu être extrait du PDF"
            )
        
        return PDFUploadResponse(
            success=True,
            text=extracted_text,
            message=f"Texte extrait avec succès ({len(extracted_text)} caractères)"
        )
        
    except Exception as e:
        return PDFUploadResponse(
            success=False,
            text="",
            message=f"Erreur lors de l'extraction: {str(e)}"
        ) 