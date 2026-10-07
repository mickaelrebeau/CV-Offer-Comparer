from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class ComparisonRequest(BaseModel):
    offer_text: str
    cv_text: str
    # Lien de l'annonce (offre importée depuis son URL), conservé dans l'historique
    offer_url: Optional[str] = None
    # Réanalyse avec un CV mis à jour : l'offre de cette comparaison est reprise telle quelle
    parent_comparison_id: Optional[UUID] = None
    # Candidature suivie à laquelle rattacher l'analyse (réanalyse : celle de la version précédente)
    application_id: Optional[UUID] = None

class ComparisonItem(BaseModel):
    id: str
    category: str
    offerText: str
    cvText: Optional[str] = None
    status: str  # 'match', 'missing', 'unclear'
    confidence: float
    suggestions: Optional[List[str]] = None

class CategoryStats(BaseModel):
    description: str
    color: str
    total: int
    matches: int
    missing: int
    unclear: int
    match_percentage: float

class ComparisonSummary(BaseModel):
    totalItems: int
    matches: int
    missing: int
    unclear: int
    matchPercentage: float
    categoryStats: Optional[Dict[str, Dict[str, Any]]] = None

class ComparisonResponse(BaseModel):
    items: List[ComparisonItem]
    summary: ComparisonSummary 