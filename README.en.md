# Talento

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mickaelrebeau/CV-Offer-Comparer)](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues)

**[Lire en français](README.md)**

Open-source web app (**Talento**) that compares a résumé (CV) with a job offer using **Gemini**: matches, gaps, ATS-oriented suggestions, and an interview simulator.

> Repository name on GitHub remains `CV-Offer-Comparer`; the product brand is **Talento**.

**Live demo:** [cv-compare.up.railway.app](https://cv-compare.up.railway.app)

---

## Features

- ATS-style CV ↔ job analysis (progressive SSE streaming)
- Concrete suggestions to strengthen the CV
- Free trial (Redis-backed limit)
- Email/password auth + **Google OAuth**
- Personalized interview simulator
- PDF upload and plain-text input
- Comparison history for signed-in users (Postgres)

## Stack

| Layer | Tech |
|--------|------|
| Frontend | Vue 3, TypeScript, Pinia, Tailwind, Vite |
| Backend | FastAPI, SQLAlchemy, Redis |
| Auth | Custom JWT + Google OAuth |
| DB | PostgreSQL |
| AI | Google Gemini (`google-genai`) |
| Analytics | PostHog (optional) |
| Deploy | Railway (Docker) |

## Architecture

```
CV-Offer-Comparer/
├── frontend/          # Vue 3 SPA
├── backend/           # FastAPI API
│   ├── app/
│   │   ├── routers/   # auth, compare, comparisons, interview…
│   │   ├── services/  # Gemini, auth, Redis…
│   │   └── models/
│   ├── Dockerfile
│   └── requirements.txt
├── documentation/     # Getting-started guides
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── LICENSE            # MIT
```

## Prerequisites

- Node.js 20+ and [pnpm](https://pnpm.io)
- Python 3.11+
- PostgreSQL and Redis (local or Railway)
- A [Google AI Studio](https://aistudio.google.com/apikey) API key
- (Optional) Google OAuth client for “Continue with Google”
- (Optional) PostHog project for product analytics

## Quick start

### 1. Clone

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
# Edit .env (GOOGLE_API_KEY, DATABASE_URL, REDIS_URL, SECRET_KEY…)
uvicorn main:app --reload
```

API: http://localhost:8000 — docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
pnpm install
cp env.example .env
# VITE_API_URL=http://localhost:8000
# Optional: VITE_POSTHOG_PROJECT_TOKEN + VITE_POSTHOG_HOST
pnpm dev
```

App: http://localhost:3000 (or the Vite port shown)

### Essential variables

**Backend** (`backend/.env`) — see `backend/env.example`:

- `GOOGLE_API_KEY`, `GEMINI_MODEL`
- `DATABASE_URL`, `REDIS_URL`
- `SECRET_KEY`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` (OAuth)
- `GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback`
- `FRONTEND_URL=http://localhost:3000`

**Frontend** (`frontend/.env`):

- `VITE_API_URL=http://localhost:8000`
- `VITE_POSTHOG_PROJECT_TOKEN` / `VITE_POSTHOG_HOST=https://eu.i.posthog.com` (optional in production builds)

Detailed guide: [documentation/STARTUP.md](documentation/STARTUP.md)

## Contributing

Contributions are welcome — bugs, docs, features, UX.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
3. Open an [issue](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues) or a PR

### Contribution ideas

- Improve Gemini prompts / analysis quality
- i18n (EN, etc.)
- Tests (backend pytest, frontend Vitest)
- Frontend accessibility and performance
- Rate limiting / security hardening

## Security

Never commit `.env` files or API keys.  
See [SECURITY.md](SECURITY.md) to report a vulnerability.

## License

Distributed under the [MIT](LICENSE) license.  
Copyright © Mickael Rebeau and contributors.

## Links

- Issues: https://github.com/mickaelrebeau/CV-Offer-Comparer/issues
- Discussions: https://github.com/mickaelrebeau/CV-Offer-Comparer/discussions (if enabled)
- Author: [@mickaelrebeau](https://github.com/mickaelrebeau)
