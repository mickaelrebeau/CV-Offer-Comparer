# Talento

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mickaelrebeau/CV-Offer-Comparer)](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues)

Application web open source (**Talento**) qui compare un CV avec une offre d’emploi grâce à **Gemini** : correspondances, lacunes, suggestions ATS, simulateur d’entretien et générateur de lettre de motivation.

**[Read in English](README.en.md)**

**Démo en ligne :** [cv-compare.up.railway.app](https://cv-compare.up.railway.app)

---

## Fonctionnalités

- Analyse ATS CV ↔ offre (streaming SSE progressif)
- Suggestions concrètes pour renforcer le CV
- Essai gratuit (limite Redis)
- Webapp installable (PWA) : manifeste, service worker, pages disponibles hors ligne
- Auth email/mot de passe + **Google OAuth**
- Simulateur d’entretien personnalisé
- Générateur de lettre de motivation (ton, longueur, langue ; copie et export `.txt` / `.md`)
- Optimiseur de CV : reformulations ciblées par offre, à accepter / rejeter / modifier, sans rien inventer (export `.txt` / `.md`, enregistrement, réanalyse)
- Upload PDF, DOCX ou TXT + saisie texte
- Historique des comparaisons, simulations, lettres et optimisations (utilisateurs connectés, Postgres)
- **Clés API personnelles (BYOK)** : Gemini, OpenAI, Claude, DeepSeek, Qwen, Kimi ou endpoint compatible OpenAI, pour continuer quand le quota Gemini de la plateforme est épuisé

## Stack

| Couche | Techno |
|--------|--------|
| Frontend | Vue 3, TypeScript, Pinia, Tailwind, Vite |
| Backend | FastAPI, SQLAlchemy, Redis |
| Auth | JWT maison + Google OAuth |
| DB | PostgreSQL |
| IA | Google Gemini (`google-genai`) ; BYOK : SDK `anthropic`, API OpenAI-compatible (`httpx`) |
| Deploy | Railway (Docker) |

## Architecture

```
CV-Offer-Comparer/
├── frontend/          # SPA Vue 3
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── routers/   # auth, compare, interview, cover-letters, free-analysis…
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
- `EMAIL_PROVIDER` (`console` en dev : liens dans les logs ; `resend` en prod avec `RESEND_API_KEY` et `EMAIL_FROM`)

### Comptes et vérification e-mail

- À l’inscription par e-mail, un lien de vérification est envoyé (valable 48 h, usage unique).
- Tant que l’adresse n’est pas vérifiée, le compte peut se connecter et consulter son historique, mais les routes IA (`compare-stream`, `interview/*`, `cover-letter`) répondent `403`. Une bannière permet de renvoyer le lien.
- Les comptes Google et les comptes créés avant cette fonctionnalité sont considérés comme vérifiés.
- Mot de passe oublié : `/forgot-password` envoie un lien (valable 60 min, usage unique). La réponse est identique que le compte existe ou non.
- Un changement de mot de passe (réinitialisation, ou suppression d’un mot de passe non vérifié lors d’une liaison Google) **déconnecte les sessions existantes** : les JWT émis avant (`iat` < `users.password_changed_at`) répondent `401` (`auth.session_expired`). Le jeton renvoyé par la réinitialisation reste valide.

**Frontend** (`frontend/.env`) :

- `VITE_API_URL=http://localhost:8000`
- `VITE_POSTHOG_PROJECT_TOKEN` / `VITE_POSTHOG_HOST=https://eu.i.posthog.com` (optionnel)

Guide détaillé : [documentation/STARTUP.md](documentation/STARTUP.md)

### Limites d’usage (rate limiting)

Les routes coûteuses (Gemini, upload) sont limitées par utilisateur **et** par IP. Au-delà, l’API répond `429 Too Many Requests` avec un header `Retry-After` (en secondes).

| Route | Limite par minute | Quota journalier (UTC, par utilisateur) |
|---|---|---|
| `POST /api/compare-stream` | user + IP | `DAILY_QUOTA_COMPARE` (50) |
| `POST /api/interview/generate-questions` | user + IP | `DAILY_QUOTA_INTERVIEW_GENERATE` (30) |
| `POST /api/interview/analyze-responses` | user + IP | `DAILY_QUOTA_INTERVIEW_ANALYZE` (30) |
| `POST /api/cover-letter` | user + IP | `DAILY_QUOTA_COVER_LETTER` (30) |
| `POST /api/cv-optimizer` | user + IP | `DAILY_QUOTA_CV_OPTIMIZER` (20) |
| `POST /api/upload-cv` | user + IP | `DAILY_QUOTA_UPLOAD` (100) |
| `PUT /api/profile/llm-credentials` | user + IP | `DAILY_QUOTA_LLM_CREDENTIALS` (50) |
| `POST /api/free-compare-stream`, `POST /api/free-upload-cv` | IP | 1 analyse gratuite par client |

- Par minute (fenêtre glissante Redis) : `RATE_LIMIT_USER_PER_MINUTE` (10) et `RATE_LIMIT_IP_PER_MINUTE` (30), par route.
- `0` = illimité ; `RATE_LIMIT_ENABLED=false` désactive tout.
- IP réelle lue dans `CLIENT_IP_HEADER` (`X-Real-IP`, posé par Railway). Derrière un autre proxy, adapter ; sans proxy, laisser vide pour utiliser l’IP de la socket.
- Sans Redis, les compteurs sont gardés en mémoire (par instance).

### Clés API personnelles (BYOK)

- Un compte connecté enregistre une clé par fournisseur depuis son profil (`/profile#llm-providers`) et en active **une seule** à la fois ; sans configuration active, l’app utilise Gemini plateforme (`GOOGLE_API_KEY`). L’essai gratuit reste toujours sur la plateforme.
- Les clés sont **chiffrées** (Fernet, `LLM_ENCRYPTION_KEYS`) et jamais renvoyées en clair. Sans `LLM_ENCRYPTION_KEYS`, la fonctionnalité est désactivée.
- Les appels sont facturés par le fournisseur de l’utilisateur, sous sa responsabilité.
- Erreurs normalisées (`code` des réponses / événements SSE) : `llm.platform_quota_exceeded`, `llm.platform_unavailable`, `llm.invalid_user_api_key`, `llm.user_provider_quota_exceeded`, `llm.provider_unavailable`, `llm.provider_rejected`, `llm.provider_refused`, `llm.unsupported_provider`.
- API : `GET /api/profile/llm-providers` (catalogue), `GET`/`PUT /api/profile/llm-credentials`, `POST …/{id}/activate`, `POST …/deactivate`, `DELETE …/{id}`.
- Configuration, rotation du secret et modèle de menace : [STARTUP](documentation/STARTUP.md) et [SECURITY.md](SECURITY.md#clés-api-personnelles-byok).

### Langues (FR / EN)

- Interface bilingue via `vue-i18n` : catalogues `frontend/src/locales/fr.json` et `en.json`.
- URL : le français est à la racine (`/login`), l’anglais sous `/en` (`/en/login`). Chaque page publique traduite est prégénérée dans les deux langues, avec `hreflang` fr / en / x-default et un sitemap généré au build.
- Langue au premier passage : celle du navigateur (sauf robots d’indexation), puis le choix du sélecteur (en-tête, profil), mémorisé dans `localStorage`.
- API : le front envoie `Accept-Language`. Les erreurs renvoient `{ "detail": "<message traduit>", "code": "<code stable>" }` ; les statuts SSE et les e-mails suivent la même langue.
- Les contenus générés par Gemini (analyse, questions) restent dans la langue du CV et de l’offre.

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
