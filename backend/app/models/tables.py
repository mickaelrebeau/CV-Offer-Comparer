"""Tous les modèles ORM : importer ce module enregistre leurs tables dans `Base.metadata`
(démarrage de l'app, migrations Alembic, tests)."""

from app.models.auth_token import AuthToken
from app.models.comparison_record import ComparisonRecord
from app.models.cover_letter_record import CoverLetterRecord
from app.models.interview_record import InterviewRecord
from app.models.llm_credential import UserLLMCredential
from app.models.saved_cv import SavedCV
from app.models.user import User

__all__ = [
    "AuthToken",
    "ComparisonRecord",
    "CoverLetterRecord",
    "InterviewRecord",
    "SavedCV",
    "User",
    "UserLLMCredential",
]
