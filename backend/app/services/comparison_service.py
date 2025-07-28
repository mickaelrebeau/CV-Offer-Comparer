import uuid
import asyncio
from typing import List, Dict, Any
from app.models.comparison import ComparisonItem, ComparisonSummary, ComparisonResponse
from app.services.ai_service import AIService
from app.utils.categorization import (
    categorize_requirement, 
    get_category_description, 
    get_category_color
)

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
            
            # Statistiques par catégorie
            category_stats = {}
            
            for i, skill in enumerate(offer_skills):
                # Calculer le progrès
                progress = (i / total_items) * 100 if total_items > 0 else 0
                
                item_id = str(uuid.uuid4())
                category = categorize_requirement(skill)
                category_description = get_category_description(category)
                category_color = get_category_color(category)
                
                # Initialiser les stats de catégorie
                if category not in category_stats:
                    category_stats[category] = {
                        "total": 0,
                        "matches": 0,
                        "missing": 0,
                        "unclear": 0
                    }
                category_stats[category]["total"] += 1
                
                # Trouver la meilleure correspondance dans le CV
                best_match = None
                best_similarity = 0.0
                
                for cv_skill in cv_skills:
                    similarity = self.ai_service.compare_semantic(skill, cv_skill)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = cv_skill
                
                # Déterminer le statut avec des seuils ajustés par catégorie
                status = self._determine_status(best_similarity, category)
                
                if status == "match":
                    matches += 1
                    category_stats[category]["matches"] += 1
                    cv_text = best_match
                elif status == "unclear":
                    unclear += 1
                    category_stats[category]["unclear"] += 1
                    cv_text = best_match if best_match else None
                else:
                    missing += 1
                    category_stats[category]["missing"] += 1
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
            
            # Ajouter les métadonnées de catégorie
            category_metadata = {}
            for category, stats in category_stats.items():
                if stats["total"] > 0:
                    category_metadata[category] = {
                        "description": get_category_description(category),
                        "color": get_category_color(category),
                        "total": stats["total"],
                        "matches": stats["matches"],
                        "missing": stats["missing"],
                        "unclear": stats["unclear"],
                        "match_percentage": (stats["matches"] / stats["total"]) * 100
                    }
            
            summary = ComparisonSummary(
                totalItems=total_items,
                matches=matches,
                missing=missing,
                unclear=unclear,
                matchPercentage=match_percentage,
                categoryStats=category_metadata
            )
            
            return ComparisonResponse(items=comparison_items, summary=summary)
            
        except Exception as e:
            print(f"Erreur lors de la comparaison: {e}")
            raise e
    
    def _determine_status(self, similarity: float, category: str) -> str:
        """Détermine le statut avec des seuils ajustés par catégorie"""
        
        # Seuils différents selon la catégorie
        thresholds = {
            "langues": {"match": 0.7, "unclear": 0.4},
            "soft skills": {"match": 0.6, "unclear": 0.3},
            "expérience et niveau": {"match": 0.8, "unclear": 0.5},
            "formation et certification": {"match": 0.7, "unclear": 0.4},
            "domaine métier": {"match": 0.6, "unclear": 0.3},
            "compétences techniques": {"match": 0.6, "unclear": 0.3},
            "autres": {"match": 0.5, "unclear": 0.3}
        }
        
        # Seuils par défaut
        default_thresholds = {"match": 0.6, "unclear": 0.3}
        category_thresholds = thresholds.get(category, default_thresholds)
        
        if similarity >= category_thresholds["match"]:
            return "match"
        elif similarity >= category_thresholds["unclear"]:
            return "unclear"
        else:
            return "missing"
    
    def get_category_breakdown(self, items: List[ComparisonItem]) -> Dict[str, Any]:
        """Retourne une analyse détaillée par catégorie"""
        
        breakdown = {}
        
        for item in items:
            category = item.category
            if category not in breakdown:
                breakdown[category] = {
                    "total": 0,
                    "matches": 0,
                    "missing": 0,
                    "unclear": 0,
                    "avg_confidence": 0.0,
                    "description": get_category_description(category),
                    "color": get_category_color(category)
                }
            
            breakdown[category]["total"] += 1
            
            if item.status == "match":
                breakdown[category]["matches"] += 1
            elif item.status == "missing":
                breakdown[category]["missing"] += 1
            else:
                breakdown[category]["unclear"] += 1
            
            breakdown[category]["avg_confidence"] += item.confidence
        
        # Calculer les moyennes et pourcentages
        for category, stats in breakdown.items():
            if stats["total"] > 0:
                stats["avg_confidence"] /= stats["total"]
                stats["match_percentage"] = (stats["matches"] / stats["total"]) * 100
                stats["missing_percentage"] = (stats["missing"] / stats["total"]) * 100
                stats["unclear_percentage"] = (stats["unclear"] / stats["total"]) * 100
        
        return breakdown 