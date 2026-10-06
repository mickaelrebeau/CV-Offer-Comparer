# Guide de démarrage local

## 1. Prérequis

- Node.js 20+ et pnpm
- Python 3.11+
- PostgreSQL + Redis (locaux ou hébergés, ex. Railway)
- Clé API Gemini : [Google AI Studio](https://aistudio.google.com/apikey)
- (Optionnel) OAuth Google Web Client pour la connexion Google

## 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
```

Renseignez au minimum dans `backend/.env` :

```env
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-flash-latest
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=change-me
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Pour Google OAuth en local, ajoutez aussi `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, et dans la console Google l’URI :

`http://localhost:8000/api/auth/google/callback`

### Clés API personnelles (BYOK, optionnel)

Les comptes connectés peuvent brancher leur propre clé LLM (Gemini, OpenAI, Claude, DeepSeek, Qwen, Kimi, endpoint compatible OpenAI) depuis leur profil. Les clés sont chiffrées au repos avec **Fernet** ; sans clé de chiffrement, la fonctionnalité est désactivée (le profil l’indique).

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

```env
LLM_ENCRYPTION_KEYS=<clé générée>
# Dev uniquement : autorise http:// et localhost comme base_url (Ollama, LM Studio…). Ignoré en production
LLM_ALLOW_PRIVATE_BASE_URLS=false
```

- Gardez cette clé **hors du dépôt** (variable Railway). La perdre rend illisibles les clés enregistrées : les utilisateurs devront les ressaisir.
- **Rotation** : placez la nouvelle clé en tête (`LLM_ENCRYPTION_KEYS=<nouvelle>,<ancienne>`), redéployez, lancez `python -m app.scripts.rotate_llm_keys`, puis retirez l’ancienne clé.
- Les appels passent alors par le fournisseur de l’utilisateur, **à ses frais** et sous sa responsabilité (conditions du fournisseur). Voir [SECURITY.md](../SECURITY.md#clés-api-personnelles-byok) pour le modèle de menace.

Démarrez :

```bash
uvicorn main:app --reload
```

- API : http://localhost:8000  
- OpenAPI : http://localhost:8000/docs  

Le schéma est mis à jour au démarrage par les migrations **Alembic** (`backend/migrations/`) : rien à lancer à la main. Une base créée avant Alembic est reconnue, mise à niveau puis marquée automatiquement.

## 3. Frontend

```bash
cd frontend
pnpm install
cp env.example .env
```

```env
VITE_API_URL=http://localhost:8000
```

```bash
pnpm dev
```

Ouvrez l’URL affichée (souvent http://localhost:3000 ou :5173).  
Si le port n’est pas 3000, alignez `FRONTEND_URL` côté backend.

## 4. Test rapide

1. Créer un compte (email) ou Google OAuth
2. Aller sur Comparateur
3. Coller une offre + un CV (ou upload PDF)
4. Lancer l’analyse (résultats en streaming)

## 5. Déploiement Railway

Le monorepo contient `frontend/Dockerfile`, `backend/Dockerfile` et `railway.json`.

- Service **backend** : `rootDirectory=/backend`, variables d’env (DB, Redis, Gemini, OAuth, `LLM_ENCRYPTION_KEYS`)
- Service **frontend** : `rootDirectory=/frontend`, **`VITE_API_URL` au build** (ARG Dockerfile)

Voir aussi `backend/env.example` et `frontend/env.production.example`.

## Dépannage

| Symptôme | Piste |
|----------|--------|
| Google OAuth → mauvais port | `FRONTEND_URL` doit matcher le port du front |
| `API key not valid` | Nouvelle clé AI Studio dans `GOOGLE_API_KEY` |
| « Quota IA de Talento épuisé » | Quota Gemini plateforme atteint : attendre, ou tester avec une clé personnelle (profil → Providers IA) |
| Profil : « clés API personnelles non activées » | Renseigner `LLM_ENCRYPTION_KEYS` |
| CORS | Ajouter l’origine front dans `ALLOWED_ORIGINS` |
| `/api/auth/google` sur le domaine front | Rebuild front avec `VITE_API_URL` pointant vers le backend |
