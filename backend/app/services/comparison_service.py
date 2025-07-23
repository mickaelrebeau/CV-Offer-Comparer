import uuid
import asyncio
from typing import List, Dict, Any
from app.models.comparison import ComparisonItem, ComparisonSummary, ComparisonResponse
from app.services.ai_service import AIService
from app.utils.categorization import categorize_requirement

class ComparisonService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def compare_cv_offer_stream(self, offer_text: str, cv_text: str, job_category: str = None):
        """Compare un CV avec une offre d'emploi avec streaming des résultats"""
        
        try:
            # Extraire les compétences de l'offre et du CV
            offer_skills = self.ai_service.extract_skills(offer_text, job_category)
            cv_skills = self.ai_service.extract_skills(cv_text, job_category)
            
            comparison_items = []
            total_items = len(offer_skills)
            matches = 0
            missing = 0
            unclear = 0
            
            for i, skill in enumerate(offer_skills):
                # Calculer le progrès
                progress = (i / total_items) * 100 if total_items > 0 else 0
                
                item_id = str(uuid.uuid4())
                category = categorize_requirement(skill)
                
                # Trouver la meilleure correspondance dans le CV
                best_match = None
                best_similarity = 0.0
                
                for cv_skill in cv_skills:
                    similarity = self.ai_service.compare_semantic(skill, cv_skill)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = cv_skill
                
                # Déterminer le statut
                if best_similarity > 0.6:
                    status = "match"
                    matches += 1
                    cv_text = best_match
                elif best_similarity > 0.3:
                    status = "unclear"
                    unclear += 1
                    cv_text = best_match if best_match else None
                else:
                    status = "missing"
                    missing += 1
                    cv_text = None
                
                # Générer des suggestions si nécessaire
                suggestions = []
                if status in ["missing", "unclear"]:
                    suggestions = self.ai_service.generate_suggestions(skill, status)
                
                item = ComparisonItem(
                    id=item_id,
                    category=category,
                    offerText=skill,
                    cvText=cv_text,
                    status=status,
                    confidence=best_similarity,
                    suggestions=suggestions if suggestions else None
                )
                comparison_items.append(item)
                
                # Petite pause pour éviter de surcharger
                await asyncio.sleep(0.1)
            
            # Calculer le pourcentage de correspondance
            match_percentage = (matches / total_items) if total_items > 0 else 0.0
            
            summary = ComparisonSummary(
                totalItems=total_items,
                matches=matches,
                missing=missing,
                unclear=unclear,
                matchPercentage=match_percentage
            )
            
            return ComparisonResponse(items=comparison_items, summary=summary)
            
        except Exception as e:
            print(f"Erreur lors de la comparaison: {e}")
            raise e 