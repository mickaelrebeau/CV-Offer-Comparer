# Quickstart

```bash
git clone https://github.com/mickaelrebeau/CV-Offer-Comparer.git
cd CV-Offer-Comparer
```

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # GOOGLE_API_KEY, DATABASE_URL, REDIS_URL, SECRET_KEY
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
cp env.example .env   # VITE_API_URL=http://localhost:8000
pnpm dev
```

Plus de détails : [STARTUP.md](./STARTUP.md) · Contribuer : [CONTRIBUTING.md](../CONTRIBUTING.md)
