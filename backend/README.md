# IGAMS Backend

Intelligent Goal Achievement Management System - Backend API

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
DATABASE_URL=postgresql://user:password@localhost:5432/igams
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
OPENAI_API_KEY=your-openai-key
```
