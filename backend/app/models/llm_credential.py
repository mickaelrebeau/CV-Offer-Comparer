import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.db import Base
from app.services.llm.catalog import get_provider


class UserLLMCredential(Base):
    """Clé API LLM personnelle (BYOK) : une par provider, une seule active par utilisateur.

    La clé n'est stockée que chiffrée (`encrypted_api_key`) et n'est jamais renvoyée au client.
    """

    __tablename__ = "user_llm_credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_llm_credentials_user_provider"),
        # Garantie en base : au plus une configuration active par utilisateur
        Index("uq_user_llm_credentials_active", "user_id", unique=True, postgresql_where=text("is_active")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hint: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Suppression du compte : la base purge les clés (ON DELETE CASCADE)
    user = relationship(
        "User",
        backref=backref("llm_credentials", cascade="all, delete-orphan", passive_deletes=True),
    )

    def to_dict(self) -> dict[str, Any]:
        provider = get_provider(self.provider)
        return {
            "id": str(self.id),
            "provider": self.provider,
            "provider_label": provider.label if provider else self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "key_hint": self.key_hint,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
