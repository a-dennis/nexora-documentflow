# Nexora - production web app

Nexora is an AI-powered productivity platform for documents, HR and careers.
This folder contains the production FastAPI application deployed on Render.

## Current status

- Phase 1 - production shell: live
- Phase 2 - Document AI: live
  (upload PDF / Word / TXT / CSV / Excel / images, AI summary, document chat,
  structured data extraction with Excel export, deep analysis)

## Run locally

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
uvicorn app:app --reload
```

Open http://127.0.0.1:8000

Without GEMINI_API_KEY the pages still load, but Document AI features stay
switched off (the site shows a friendly notice).

## Render setup

- Root Directory: nexora_web
- Build Command: pip install -r requirements.txt
- Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
- Environment variable: GEMINI_API_KEY (server-side secret - never commit it)

Auto-deploy is on: pushing to main deploys automatically.

## Health check

GET /health -> {"status": "ok", "service": "nexora"}
