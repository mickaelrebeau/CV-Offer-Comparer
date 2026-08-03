# Talento

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mickaelrebeau/CV-Offer-Comparer)](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues)

Application web open source (**Talento**) qui compare un CV avec une offre d’emploi grâce à **Gemini** : correspondances, lacunes, suggestions ATS, et simulateur d’entretien.

**[Read in English](README.en.md)**

**Démo en ligne :** [cv-compare.up.railway.app](https://cv-compare.up.railway.app)

---

## Fonctionnalités

- Analyse ATS CV ↔ offre (streaming SSE progressif)
- Suggestions concrètes pour renforcer le CV
- Essai gratuit (limite Redis)
- Auth email/mot de passe + **Google OAuth**
- Simulateur d’entretien personnalisé
- Upload PDF + saisie texte

## Stack

| Couche | Techno |
|--------|--------|
| Frontend | Vue 3, TypeScript, Pinia, Tailwind, Vite |
| Backend | FastAPI, SQLAlchemy, Redis |
| Auth | JWT maison + Google OAuth |
| DB | PostgreSQL |
| IA | Google Gemini (`google-genai`) |
| Deploy | Railway (Docker) |

## Architecture

```
CV-Offer-Comparer/
├── frontend/          # SPA Vue 3
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── routers/   # auth, compare, interview, free-analysis…
│   │   ├── services/  # Gemini, auth, Redis…
│   │   └── models/
│   ├── Dockerfile
│   └── requirements.txt
├── documentation/     # Guides démarrage
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── LICENSE            # MIT
```

## Prérequis

- Node.js 20+ et [pnpm](https://pnpm.io)
- Python 3.11+
- PostgreSQL et Redis (local ou Railway)
- Clé [Google AI Studio](https://aistudio.google.com/apikey)
- (Optionnel) Client OAuth Google pour « Continuer avec Google »

## Démarrage rapide

### 1. Cloner

```bash
git clone https://github.com/mickaelrebeau/CV-Offer-Comparer.git
cd CV-Offer-Comparer
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Éditer .env (GOOGLE_API_KEY, DATABASE_URL, REDIS_URL, SECRET_KEY…)
uvicorn main:app --reload
```

API : http://localhost:8000 — docs : http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
pnpm install
cp env.example .env
# VITE_API_URL=http://localhost:8000
pnpm dev
```

App : http://localhost:3000 (ou le port Vite affiché)

### Variables essentielles

**Backend** (`backend/.env`) — voir `backend/env.example` :

- `GOOGLE_API_KEY`, `GEMINI_MODEL`
- `DATABASE_URL`, `REDIS_URL`
- `SECRET_KEY`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` (OAuth)
- `GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback`
- `FRONTEND_URL=http://localhost:3000`

**Frontend** (`frontend/.env`) :

- `VITE_API_URL=http://localhost:8000`

Guide détaillé : [documentation/STARTUP.md](documentation/STARTUP.md)

## Contribuer

Les contributions sont les bienvenues — bugs, docs, features, UX.

1. Lire [CONTRIBUTING.md](CONTRIBUTING.md)
2. Respecter le [Code of Conduct](CODE_OF_CONDUCT.md)
3. Ouvrir une [issue](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues) ou une PR

### Idées de contributions

- Améliorer les prompts Gemini / qualité d’analyse
- i18n (EN, etc.)
- Tests (backend pytest, frontend Vitest)
- CI GitHub Actions
- Accessibilité et perf front
- Historique des comparaisons en Postgres

## Sécurité

Ne committez **jamais** de `.env` ni de clés API.  
Voir [SECURITY.md](SECURITY.md) pour signaler une vulnérabilité.

## Licence

Distribué sous licence [MIT](LICENSE).  
Copyright © Mickael Rebeau et contributeurs.

## Liens

- Issues : https://github.com/mickaelrebeau/CV-Offer-Comparer/issues
- Discussions : https://github.com/mickaelrebeau/CV-Offer-Comparer/discussions (si activées)
- Auteur : [@mickaelrebeau](https://github.com/mickaelrebeau)
