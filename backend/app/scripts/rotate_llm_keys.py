"""Rechiffre toutes les clés API utilisateur avec la clé Fernet principale.

Rotation de LLM_ENCRYPTION_KEYS :
1. générer une clé : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
2. la placer EN TÊTE : LLM_ENCRYPTION_KEYS=<nouvelle>,<ancienne> puis redéployer
3. lancer : python -m app.scripts.rotate_llm_keys
4. retirer l'ancienne clé de LLM_ENCRYPTION_KEYS et redéployer
"""

from sqlalchemy import select

from app.db import SessionLocal
from app.models.llm_credential import UserLLMCredential
from app.models.user import User  # noqa: F401 — relation User chargée par l'ORM
from app.services.llm.crypto import rotate


def main() -> int:
    with SessionLocal() as db:
        credentials = db.scalars(select(UserLLMCredential)).all()
        for credential in credentials:
            credential.encrypted_api_key = rotate(credential.encrypted_api_key)
        db.commit()
    print(f"{len(credentials)} clé(s) rechiffrée(s) avec la clé principale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
