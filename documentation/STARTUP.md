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

Démarrez :

```bash
uvicorn main:app --reload
```

- API : http://localhost:8000  
- OpenAPI : http://localhost:8000/docs  

Les tables (`users`, etc.) sont créées au démarrage via SQLAlchemy.

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

- Service **backend** : `rootDirectory=/backend`, variables d’env (DB, Redis, Gemini, OAuth)
- Service **frontend** : `rootDirectory=/frontend`, **`VITE_API_URL` au build** (ARG Dockerfile)

Voir aussi `backend/env.example` et `frontend/env.production.example`.

## Dépannage

| Symptôme | Piste |
|----------|--------|
| Google OAuth → mauvais port | `FRONTEND_URL` doit matcher le port du front |
| `API key not valid` | Nouvelle clé AI Studio dans `GOOGLE_API_KEY` |
| CORS | Ajouter l’origine front dans `ALLOWED_ORIGINS` |
| `/api/auth/google` sur le domaine front | Rebuild front avec `VITE_API_URL` pointant vers le backend |
