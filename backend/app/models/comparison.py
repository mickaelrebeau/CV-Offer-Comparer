from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ComparisonRequest(BaseModel):
    offer_text: str
    cv_text: str

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