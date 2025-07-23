import PyPDF2
import pdfplumber
import io
from fastapi import HTTPException, UploadFile

class UploadService:
    def extract_text_from_pdf(self, pdf_file: UploadFile) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            # Lire le contenu du fichier
            content = pdf_file.file.read()
            
            # Essayer d'abord avec pdfplumber (meilleur pour les PDF complexes)
            try:
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text.strip()
            except Exception as e:
                print(f"pdfplumber failed: {e}")
                
                # Fallback avec PyPDF2
                try:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
                except Exception as e2:
                    print(f"PyPDF2 failed: {e2}")
                    raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF")
                    
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur lors du traitement du PDF: {str(e)}") 