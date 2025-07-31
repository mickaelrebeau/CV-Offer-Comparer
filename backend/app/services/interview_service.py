from typing import List, Dict, Any, Optional
from app.services.ai_service import AIService
from app.services.upload_service import UploadService
import json
import uuid
from datetime import datetime

class InterviewService:
    def __init__(self):
        self.ai_service = AIService()
        self.upload_service = UploadService()
    
    async def generate_interview_questions(self, cv_file: bytes, job_text: str, num_questions: int = 10) -> Dict[str, Any]:
        """
        Génère des questions d'entretien basées sur le CV et l'offre d'emploi.
        
        Args:
            cv_file: Fichier CV en bytes
            job_text: Fichier offre d'emploi en texte
            num_questions: Nombre de questions à générer
            
        Returns:
            Dictionnaire contenant les questions et les métadonnées
        """
        try:
            # Extraire le texte des fichiers
            cv_text = await self._extract_text_from_file(cv_file)
            print(f"Texte CV extrait: {len(cv_text)} caractères")
            
            if not cv_text.strip():
                print("ERREUR: Le texte du CV est vide")
                return {
                    "success": False,
                    "error": "Impossible d'extraire le texte du CV",
                    "message": "Le fichier CV semble être vide ou corrompu"
                }
            
            if not job_text.strip():
                print("ERREUR: Le texte de l'offre d'emploi est vide")
                return {
                    "success": False,
                    "error": "Le texte de l'offre d'emploi est vide",
                    "message": "Veuillez fournir une description de l'offre d'emploi"
                }
            
            # Générer les questions avec l'IA
            print("Appel du service IA pour générer les questions...")
            questions = self.ai_service.generate_interview_questions(
                cv_text, 
                job_text, 
                num_questions
            )
            
            # Créer une session d'entretien
            interview_session = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "num_questions": len(questions),
                "estimated_time": len(questions) * 2,  # 2 minutes par question
                "questions": questions
            }
            
            return {
                "success": True,
                "interview_session": interview_session,
                "message": f"{len(questions)} questions générées avec succès"
            }
            
        except Exception as e:
            print(f"Erreur dans generate_interview_questions: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de la génération des questions"
            }
    
    async def _extract_text_from_file(self, file_content: bytes) -> str:
        """
        Extrait le texte d'un fichier (PDF ou texte).
        """
        try:
            print("Tentative d'extraction de texte depuis le fichier...")
            
            # Essayer d'abord comme PDF
            try:
                text = await self.upload_service.extract_text_from_pdf(file_content)
                print(f"Texte extrait depuis PDF: {len(text)} caractères")
                return text
            except Exception as pdf_error:
                print(f"Échec de l'extraction PDF: {pdf_error}")
                
                # Si ça échoue, traiter comme du texte brut
                try:
                    text = file_content.decode('utf-8')
                    print(f"Texte extrait depuis UTF-8: {len(text)} caractères")
                    return text
                except UnicodeDecodeError:
                    text = file_content.decode('latin-1')
                    print(f"Texte extrait depuis Latin-1: {len(text)} caractères")
                    return text
                    
        except Exception as e:
            print(f"Erreur lors de l'extraction de texte: {e}")
            raise Exception(f"Impossible d'extraire le texte du fichier: {e}")
    
    async def analyze_responses(self, questions: list, answers: list, cv_text: str, job_text: str) -> Dict[str, Any]:
        """
        Analyse les réponses d'entretien avec l'IA.
        
        Args:
            questions: Liste des questions posées
            answers: Liste des réponses données
            cv_text: Texte du CV
            job_text: Texte de l'offre d'emploi
            
        Returns:
            Dictionnaire contenant l'analyse
        """
        try:
            result = self.ai_service.analyze_interview_responses(
                questions, 
                answers, 
                cv_text, 
                job_text
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'analyse des réponses"
            }
    