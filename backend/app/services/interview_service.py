from typing import Dict, Any
from app.services.ai_service import ai_service
import uuid
from datetime import datetime

class InterviewService:
    def __init__(self):
        self.ai_service = ai_service

    
    async def generate_interview_questions(self, cv_text: str, job_text: str, num_questions: int = 10) -> Dict[str, Any]:
        """
        Génère des questions d'entretien basées sur le CV et l'offre d'emploi.
        
        Args:
            cv_text: Texte du CV (déjà extrait du PDF/TXT)
            job_text: Fichier offre d'emploi en texte
            num_questions: Nombre de questions à générer
            
        Returns:
            Dictionnaire contenant les questions et les métadonnées
        """
        try:
            if not cv_text.strip():
                print("ERREUR: Le texte du CV est vide")
                return {
                    "success": False,
                    "error": "Impossible d'extraire le texte du CV",
                    "code": "upload.empty_file",
                }
            
            if not job_text.strip():
                print("ERREUR: Le texte de l'offre d'emploi est vide")
                return {
                    "success": False,
                    "error": "Le texte de l'offre d'emploi est vide",
                    "code": "interview.job_empty",
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
            }
            
        except Exception as e:
            print(f"Erreur dans generate_interview_questions: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "code": "interview.questions_failed",
            }
    
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
                "code": "interview.analysis_failed",
            }
    