from fastapi import APIRouter, Depends, UploadFile, File
from app.models.upload import PDFUploadResponse
from app.services.upload_service import UploadService
from app.services.auth_service import AuthService
from app.services.rate_limit_service import rate_limit

router = APIRouter()
auth_service = AuthService()
upload_service = UploadService()

@router.post(
    "/upload-cv",
    response_model=PDFUploadResponse,
    dependencies=[Depends(rate_limit("upload", "DAILY_QUOTA_UPLOAD"))],
)
async def upload_cv_pdf(
    file: UploadFile = File(...),
    user=Depends(auth_service.verify_token)
):
    """Upload et extraction de texte d'un CV PDF"""
    return await upload_service.pdf_upload_response(file)
