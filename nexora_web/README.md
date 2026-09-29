# Nexora - web production shell

FastAPI production shell for Nexora (Phase 1). Deployed on Render.

## Render settings

- Root Directory: `nexora_web`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Python: 3.13 (from `.python-version`)

## Routes

| Path | Purpose |
| --- | --- |
| `/` | Home |
| `/document-ai` | Document AI section (placeholder) |
| `/hr-career` | HR & Career section (placeholder) |
| `/resume-builder` | Resume Builder + ATS Optimizer (featured placeholder) |
| `/jd-builder` | JD Builder + Recruitment Optimizer (featured placeholder) |
| `/health` | Health check: `{"status":"ok","service":"nexora"}` |

## Run locally

```
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open http://127.0.0.1:8000
