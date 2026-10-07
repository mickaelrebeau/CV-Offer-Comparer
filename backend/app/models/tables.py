"""Tous les modèles ORM : importer ce module enregistre leurs tables dans `Base.metadata`
(démarrage de l'app, migrations Alembic, tests)."""

from app.models.application_record import ApplicationRecord
from app.models.auth_token import AuthToken
from app.models.comparison_record import ComparisonRecord
from app.models.cover_letter_record import CoverLetterRecord
from app.models.cv_optimization_record import CvOptimizationRecord
from app.models.interview_record import InterviewRecord
from app.models.llm_credential import UserLLMCredential
from app.models.saved_cv import SavedCV
from app.models.user import User

__all__ = [
    "ApplicationRecord",
    "AuthToken",
    "ComparisonRecord",
    "CoverLetterRecord",
    "CvOptimizationRecord",
    "InterviewRecord",
    "SavedCV",
    "User",
    "UserLLMCredential",
]
