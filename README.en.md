# Talento

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mickaelrebeau/CV-Offer-Comparer)](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues)

**[Lire en français](README.md)**

Open-source web app (**Talento**) that compares a résumé (CV) with a job offer using **Gemini**: matches, gaps, ATS-oriented suggestions, an interview simulator and a cover letter generator.

> Repository name on GitHub remains `CV-Offer-Comparer`; the product brand is **Talento**.

**Live demo:** [cv-compare.up.railway.app](https://cv-compare.up.railway.app)

---

## Features

- ATS-style CV ↔ job analysis (progressive SSE streaming)
- Concrete suggestions to strengthen the CV
- Free trial (Redis-backed limit)
- Installable web app (PWA): manifest, service worker, pages available offline
- Email/password auth + **Google OAuth**
- Personalized interview simulator
- Cover letter generator (tone, length, language; copy and `.txt` / `.md` export)
- Resume optimizer: targeted rewrites per job offer, to accept / reject / edit, without inventing anything (`.txt` / `.md` export, save, re-analysis)
- Application tracking (list and Kanban): status, notes, and the analyses / letters / simulations linked to each job offer
- PDF, DOCX or TXT upload and plain-text input
- Comparison, interview, cover letter and resume optimization history for signed-in users (Postgres)
- **Bring your own API key (BYOK)**: Gemini, OpenAI, Claude, DeepSeek, Qwen, Kimi or any OpenAI-compatible endpoint, to keep going when the platform Gemini quota is exhausted

## Stack

| Layer | Tech |
|--------|------|
| Frontend | Vue 3, TypeScript, Pinia, Tailwind, Vite |
| Backend | FastAPI, SQLAlchemy, Redis |
| Auth | Custom JWT + Google OAuth |
| DB | PostgreSQL |
| AI | Google Gemini (`google-genai`); BYOK: `anthropic` SDK, OpenAI-compatible API (`httpx`) |
| Analytics | PostHog (optional) |
| Deploy | Railway (Docker) |

## Architecture

```
CV-Offer-Comparer/
├── frontend/          # Vue 3 SPA
├── backend/           # FastAPI API
│   ├── app/
│   │   ├── routers/   # auth, compare, comparisons, interview, cover-letters…
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
- `EMAIL_PROVIDER` (`console` in dev: links printed in logs; `resend` in production with `RESEND_API_KEY` and `EMAIL_FROM`)

### Accounts and email verification

- Email sign-ups receive a verification link (valid 48 h, single use).
- Until the address is verified, the account can sign in and see its history, but AI routes (`compare-stream`, `interview/*`, `cover-letter`) answer `403`. A banner lets the user resend the link.
- Google accounts and accounts created before this feature are considered verified.
- Forgot password: `/forgot-password` sends a link (valid 60 min, single use). The response is identical whether the account exists or not.
- A password change (reset, or removal of an unverified password when linking Google) **signs out existing sessions**: JWTs issued before it (`iat` < `users.password_changed_at`) get a `401` (`auth.session_expired`). The token returned by the reset stays valid.

**Frontend** (`frontend/.env`):

- `VITE_API_URL=http://localhost:8000`
- `VITE_POSTHOG_PROJECT_TOKEN` / `VITE_POSTHOG_HOST=https://eu.i.posthog.com` (optional in production builds)

Detailed guide: [documentation/STARTUP.md](documentation/STARTUP.md)

### Usage limits (rate limiting)

Costly routes (Gemini, upload) are limited per user **and** per IP. Beyond the limit, the API answers `429 Too Many Requests` with a `Retry-After` header (seconds).

| Route | Per-minute limit | Daily quota (UTC, per user) |
|---|---|---|
| `POST /api/compare-stream` | user + IP | `DAILY_QUOTA_COMPARE` (50) |
| `POST /api/interview/generate-questions` | user + IP | `DAILY_QUOTA_INTERVIEW_GENERATE` (30) |
| `POST /api/interview/analyze-responses` | user + IP | `DAILY_QUOTA_INTERVIEW_ANALYZE` (30) |
| `POST /api/cover-letter` | user + IP | `DAILY_QUOTA_COVER_LETTER` (30) |
| `POST /api/cv-optimizer` | user + IP | `DAILY_QUOTA_CV_OPTIMIZER` (20) |
| `POST /api/applications` | user + IP | `DAILY_QUOTA_APPLICATIONS` (100) |
| `PUT /api/profile/llm-credentials` | user + IP | `DAILY_QUOTA_LLM_CREDENTIALS` (50) |
| `POST /api/upload-cv` | user + IP | `DAILY_QUOTA_UPLOAD` (100) |
| `POST /api/free-compare-stream`, `POST /api/free-upload-cv` | IP | 1 free analysis per client |

- Per minute (Redis sliding window): `RATE_LIMIT_USER_PER_MINUTE` (10) and `RATE_LIMIT_IP_PER_MINUTE` (30), per route.
- `0` = unlimited; `RATE_LIMIT_ENABLED=false` disables everything.
- Real client IP is read from `CLIENT_IP_HEADER` (`X-Real-IP`, set by Railway). Adjust behind another proxy; leave empty without a proxy to use the socket IP.
- Without Redis, counters are kept in memory (per instance).

### Personal API keys (BYOK)

- A signed-in account saves one key per provider from its profile (`/en/profile#llm-providers`) and activates **only one** at a time; with no active configuration, the app uses the platform Gemini stack (`GOOGLE_API_KEY`). The free trial always stays on the platform.
- Keys are **encrypted** (Fernet, `LLM_ENCRYPTION_KEYS`) and never returned in clear. Without `LLM_ENCRYPTION_KEYS`, the feature is disabled.
- Calls are billed by the user's provider, under the user's responsibility.
- Normalized errors (`code` in responses / SSE events): `llm.platform_quota_exceeded`, `llm.platform_unavailable`, `llm.invalid_user_api_key`, `llm.user_provider_quota_exceeded`, `llm.provider_unavailable`, `llm.provider_rejected`, `llm.provider_refused`, `llm.unsupported_provider`.
- API: `GET /api/profile/llm-providers` (catalog), `GET`/`PUT /api/profile/llm-credentials`, `POST …/{id}/activate`, `POST …/deactivate`, `DELETE …/{id}`.
- Setup, secret rotation and threat model: [STARTUP](documentation/STARTUP.md) (French) and [SECURITY.md](SECURITY.md#clés-api-personnelles-byok).

### Languages (FR / EN)

- Bilingual UI with `vue-i18n`: catalogs `frontend/src/locales/fr.json` and `en.json`.
- URLs: French at the root (`/login`), English under `/en` (`/en/login`). Every translated public page is prerendered in both languages, with fr / en / x-default `hreflang` and a sitemap generated at build time.
- Language on first visit: the browser’s (except for search engine bots), then the switcher choice (header, profile), stored in `localStorage`.
- API: the frontend sends `Accept-Language`. Errors return `{ "detail": "<translated message>", "code": "<stable code>" }`; SSE statuses and emails follow the same language.
- Content generated by Gemini (analysis, questions) stays in the language of the resume and job offer.

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
