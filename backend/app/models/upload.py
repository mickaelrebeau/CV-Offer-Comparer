from pydantic import BaseModel

class PDFUploadResponse(BaseModel):
    success: bool
    text: str
    message: str 