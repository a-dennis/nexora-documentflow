"""
Nexora - production application (Phases 1-3: shell, Document AI, HR & Career).

FastAPI website serving the Nexora landing pages plus the working
Document AI workspace: upload a document, summarize it, chat with it,
extract structured data (Excel export) and run a deep analysis.

Routes:
  /                Home
  /document-ai     Document AI workspace (live)
  /hr-career       HR & Career hub (live)
  /resume-builder  Resume Builder (AI, live) - same as /career/resume-builder
  /jd-builder      JD Builder (AI, live) - same as /career/jd-builder
  /health          JSON health check for Render

API routes (Document AI):
  POST /api/documents                     upload a document
  GET  /api/documents/{doc_id}            document info + text preview
  POST /api/documents/{doc_id}/summary    AI summary
  POST /api/documents/{doc_id}/chat       AI Q&A on the document
  POST /api/documents/{doc_id}/extract    AI structured data extraction (JSON)
  POST /api/documents/{doc_id}/analyze    AI deep analysis
  GET  /api/documents/{doc_id}/export.xlsx  Excel export of last extraction

Phase 3 (HR & Career):
  /career/{slug}   8 AI career tools (resume/JD builders, analyzers, ATS, cover letter, offer)
  /hr/calculators  CTC, take-home, increment, gratuity, notice period
  /hr/documents    8 HR document templates as Word downloads
  POST /api/career/{slug}        run a career AI tool
  POST /api/hr/document/{slug}   generate an HR document (.docx)
  POST /api/download-docx        convert AI output to .docx

Secrets: GEMINI_API_KEY is read from the environment only. Never commit it.
"""

import io
import os
import re
import time
import uuid
import json
import threading
import traceback
from collections import defaultdict, deque

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

app = FastAPI(title="Nexora", docs_url=None, redoc_url=None, openapi_url=None)

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Fast, cost-efficient model first; fallbacks protect against renames.
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-flash-lite-latest", "gemini-3.1-flash-lite"]

MAX_UPLOAD_BYTES = 12 * 1024 * 1024        # 12 MB per file
MAX_TEXT_CHARS = 120_000                   # text sent to the AI per request
MAX_DOCS_IN_MEMORY = 25                    # in-memory document store cap
DOC_TTL_SECONDS = 6 * 3600                 # documents expire after 6 hours
RATE_LIMIT_AI_PER_HOUR = 40                # AI calls per IP per hour

# ----------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------

NAV_ITEMS = [
    ("/", "Home"),
    ("/document-ai", "Document AI"),
    ("/hr-career", "HR &amp; Career"),
    ("/resume-builder", "Resume Builder"),
    ("/jd-builder", "JD Builder"),
]

# ----------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------

CSS = """
:root {
  --ink: #0f172a;
  --muted: #52637a;
  --line: #e3e8f0;
  --bg: #f6f8fb;
  --card: #ffffff;
  --accent: #1d4ed8;
  --accent-dark: #1a43b8;
  --tint: #eef4ff;
  --green: #0e7a3d;
  --green-tint: #e9f7ef;
  --red: #b42318;
  --red-tint: #fef3f2;
  --radius: 14px;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.55;
}
.container { max-width: 1080px; margin: 0 auto; padding: 0 20px; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ---------- top navigation ---------- */
.topnav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(6px);
}
.nav-inner { display: flex; align-items: center; min-height: 60px; gap: 16px; }
.brand {
  font-size: 22px; font-weight: 800; letter-spacing: 0.2px;
  color: var(--ink); margin-right: auto;
}
.brand:hover { text-decoration: none; }
.brand span { color: var(--accent); }
.navlinks { display: flex; align-items: center; gap: 4px; }
.navlinks a {
  color: var(--ink); font-size: 15px; font-weight: 500;
  padding: 9px 12px; border-radius: 8px; white-space: nowrap;
}
.navlinks a:hover { background: var(--tint); text-decoration: none; }
.navlinks a.active { color: var(--accent); background: var(--tint); }
.navtoggle { display: none; }
.burger { display: none; }

@media (max-width: 760px) {
  .burger {
    display: flex; flex-direction: column; justify-content: center;
    gap: 5px; width: 44px; height: 44px; padding: 10px;
    cursor: pointer; border-radius: 8px;
  }
  .burger:hover { background: var(--tint); }
  .burger span {
    display: block; height: 2px; background: var(--ink); border-radius: 2px;
  }
  .navlinks {
    display: none; position: absolute; top: 60px; left: 0; right: 0;
    flex-direction: column; align-items: stretch; gap: 2px;
    background: #ffffff; border-bottom: 1px solid var(--line);
    padding: 10px 16px 16px;
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
  }
  .navlinks a { padding: 13px 12px; font-size: 16px; }
  .navtoggle:checked ~ .navlinks { display: flex; }
}

/* ---------- hero ---------- */
.hero { padding: 64px 0 28px; text-align: center; }
.kicker {
  margin: 0 0 10px; font-size: 13px; font-weight: 700;
  letter-spacing: 1.6px; text-transform: uppercase; color: var(--accent);
}
.hero h1 {
  margin: 0 auto 14px; max-width: 720px;
  font-size: clamp(30px, 5vw, 44px); line-height: 1.15; letter-spacing: -0.5px;
}
.lede {
  margin: 0 auto; max-width: 620px;
  font-size: clamp(16px, 2.4vw, 19px); color: var(--muted);
}

/* ---------- sections & cards ---------- */
.section { padding: 36px 0 8px; }
.section-head { margin-bottom: 20px; }
.section-head.center { text-align: center; }
.section-head h2 {
  margin: 0 0 6px; font-size: clamp(21px, 3vw, 26px); letter-spacing: -0.3px;
}
.section-head p { margin: 0; color: var(--muted); font-size: 16px; }
.grid { display: grid; gap: 16px; grid-template-columns: repeat(2, 1fr); }
.grid.four { grid-template-columns: repeat(4, 1fr); }
.grid.three { grid-template-columns: repeat(3, 1fr); }
@media (max-width: 900px) { .grid.four { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) {
  .grid, .grid.three, .grid.four { grid-template-columns: 1fr; }
}
.card {
  background: var(--card); border: 1px solid var(--line);
  border-radius: var(--radius); padding: 24px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.card.pad-sm { padding: 18px; }
a.card-link { display: block; color: inherit; }
a.card-link:hover { text-decoration: none; border-color: #c4d4f5; box-shadow: 0 6px 18px rgba(29, 78, 216, 0.09); }
.card-icon {
  width: 42px; height: 42px; border-radius: 10px;
  background: var(--tint); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
}
.card h3 { margin: 0 0 6px; font-size: 18px; }
.card p { margin: 0 0 14px; color: var(--muted); font-size: 15px; }
.card p:last-child { margin-bottom: 0; }
.tag {
  display: inline-block; font-size: 12px; font-weight: 700;
  letter-spacing: 0.4px; text-transform: uppercase;
  padding: 4px 9px; border-radius: 999px;
}
.tag.soon { background: #f1f5f9; color: var(--muted); border: 1px solid var(--line); }
.tag.featured { background: var(--green-tint); color: var(--green); border: 1px solid #cdeeda; }
.tag.live { background: var(--green-tint); color: var(--green); border: 1px solid #cdeeda; }

/* ---------- buttons ---------- */
.btn {
  display: inline-block; min-height: 46px; padding: 12px 20px;
  font-size: 15px; font-weight: 600; border-radius: 10px;
  background: var(--accent); color: #ffffff; border: 1px solid var(--accent);
  cursor: pointer;
}
.btn:hover { background: var(--accent-dark); text-decoration: none; }
.btn.ghost { background: #ffffff; color: var(--accent); border: 1px solid #c4d4f5; }
.btn.ghost:hover { background: var(--tint); }
.btn.disabled, .btn.disabled:hover, .btn:disabled {
  background: #eef2f7; border-color: var(--line); color: var(--muted);
  cursor: default; text-decoration: none;
}

/* ---------- split feature lists ---------- */
.split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 640px) { .split { grid-template-columns: 1fr; } }
.checklist { margin: 0; padding: 0; list-style: none; }
.checklist li {
  padding: 7px 0 7px 28px; position: relative;
  color: var(--ink); font-size: 15px; border-bottom: 1px dashed var(--line);
}
.checklist li:last-child { border-bottom: none; }
.checklist li::before {
  content: "\\2713"; position: absolute; left: 4px; top: 7px;
  color: var(--green); font-weight: 700;
}
.note {
  margin-top: 18px; padding: 14px 16px; font-size: 14px; color: var(--muted);
  background: #ffffff; border: 1px solid var(--line); border-radius: 10px;
}

/* ---------- page hero (inner pages) ---------- */
.page-hero { padding: 48px 0 8px; }
.page-hero h1 { margin: 0 0 10px; font-size: clamp(26px, 4vw, 34px); letter-spacing: -0.4px; }
.page-hero p { margin: 0; max-width: 640px; color: var(--muted); font-size: 17px; }

/* ---------- document workspace ---------- */
.dropzone {
  border: 2px dashed #c4d4f5; border-radius: var(--radius);
  background: #ffffff; padding: 40px 24px; text-align: center;
  cursor: pointer; transition: border-color .15s, background .15s;
}
.dropzone:hover, .dropzone.drag { border-color: var(--accent); background: var(--tint); }
.dropzone h3 { margin: 10px 0 4px; font-size: 19px; }
.dropzone p { margin: 0; color: var(--muted); font-size: 14px; }
.filetypes { margin-top: 14px; font-size: 13px; color: var(--muted); }
.workspace { display: none; }
.workspace.on { display: block; }
.docbar {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
  background: #ffffff; border: 1px solid var(--line);
  border-radius: var(--radius); padding: 14px 18px;
}
.docbar .name { font-weight: 700; font-size: 16px; word-break: break-all; }
.docbar .meta { color: var(--muted); font-size: 13px; }
.docbar .spacer { margin-left: auto; }
.tabs {
  display: flex; gap: 4px; margin: 18px 0 0; flex-wrap: wrap;
  border-bottom: 1px solid var(--line);
}
.tabs button {
  border: none; background: none; padding: 11px 16px; font-size: 15px;
  font-weight: 600; color: var(--muted); cursor: pointer;
  border-bottom: 2px solid transparent; min-height: 44px;
}
.tabs button:hover { color: var(--ink); }
.tabs button.active { color: var(--accent); border-bottom-color: var(--accent); }
.pane { display: none; padding: 20px 0 8px; }
.pane.on { display: block; }
.result {
  background: #ffffff; border: 1px solid var(--line);
  border-radius: var(--radius); padding: 20px; margin-top: 16px;
  font-size: 15px; white-space: pre-wrap; word-break: break-word;
}
.result:empty { display: none; }
.result h4 { margin: 18px 0 6px; }
.result h4:first-child { margin-top: 0; }
.chatlog { display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }
.msg {
  max-width: 85%; padding: 12px 16px; border-radius: 14px;
  font-size: 15px; white-space: pre-wrap; word-break: break-word;
}
.msg.user { align-self: flex-end; background: var(--accent); color: #fff; }
.msg.ai { align-self: flex-start; background: #ffffff; border: 1px solid var(--line); }
.chatrow { display: flex; gap: 8px; margin-top: 14px; }
.chatrow input {
  flex: 1; min-height: 46px; padding: 12px 14px; font-size: 15px;
  border: 1px solid var(--line); border-radius: 10px; font-family: inherit;
}
.chatrow input:focus { outline: 2px solid #c4d4f5; border-color: var(--accent); }
.sugg { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.sugg button {
  border: 1px solid #c4d4f5; background: #ffffff; color: var(--accent);
  border-radius: 999px; padding: 8px 14px; font-size: 13px; font-weight: 600;
  cursor: pointer; min-height: 38px;
}
.sugg button:hover { background: var(--tint); }
table.kv {
  width: 100%; border-collapse: collapse; margin-top: 14px;
  background: #ffffff; border: 1px solid var(--line); border-radius: 10px;
  font-size: 14px;
}
table.kv th, table.kv td {
  text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line);
  vertical-align: top; word-break: break-word;
}
table.kv th { background: var(--tint); font-weight: 700; }
.spin {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid #c4d4f5; border-top-color: var(--accent);
  border-radius: 50%; animation: rot .8s linear infinite; vertical-align: -3px;
}
@keyframes rot { to { transform: rotate(360deg); } }
.err {
  background: var(--red-tint); color: var(--red);
  border: 1px solid #f6d3d0; border-radius: 10px;
  padding: 12px 16px; font-size: 14px; margin-top: 14px;
}
.err:empty { display: none; }
.ai-off {
  background: #fffaeb; border: 1px solid #f5e3b3; color: #7a5d00;
  border-radius: 10px; padding: 14px 16px; font-size: 14px; margin-top: 16px;
}

/* ---------- forms (Phase 3) ---------- */
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; font-weight: 600; color: var(--ink); margin-bottom: 5px; }
.field input, .field textarea, .field select {
  width: 100%; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px;
  font-size: 14px; font-family: inherit; background: #ffffff; color: var(--ink);
}
.field textarea { min-height: 110px; resize: vertical; line-height: 1.5; }
.field input:focus, .field textarea:focus, .field select:focus {
  outline: 2px solid #c4d4f5; border-color: var(--accent);
}
.frow { display: grid; gap: 12px; grid-template-columns: 1fr 1fr; }
@media (max-width: 720px) { .frow { grid-template-columns: 1fr; } }
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; align-items: center; }
.pill-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
.pill-tabs button {
  border: 1px solid var(--line); background: #ffffff; color: var(--muted);
  border-radius: 999px; padding: 8px 14px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.pill-tabs button.active { background: var(--accent); border-color: var(--accent); color: #ffffff; }
.hint { font-size: 13px; color: var(--muted); margin-top: 4px; }
.srcbox { border: 1px dashed var(--line); border-radius: 10px; padding: 12px; margin-bottom: 16px; }
.attached { font-size: 13px; color: var(--green, #067647); font-weight: 600; margin-top: 6px; }
h2.sech { font-size: 22px; margin: 34px 0 14px; }
.result ul { margin: 6px 0 12px 20px; }
.result li { margin-bottom: 4px; }
.result p { margin: 8px 0; }
/* ---------- footer ---------- */
.footer {
  margin-top: 56px; padding: 28px 0 40px;
  border-top: 1px solid var(--line); color: var(--muted); font-size: 14px;
}
.footer .row { display: flex; flex-wrap: wrap; gap: 8px 24px; align-items: center; }
.footer .brand { font-size: 17px; margin: 0; }
"""

# ----------------------------------------------------------------------
# Small inline SVG icons (24x24, currentColor)
# ----------------------------------------------------------------------

ICONS = {
    "doc": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    "briefcase": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "resume": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="10" cy="13" r="2"/><path d="M6 19c0-2 1.8-3 4-3s4 1 4 3"/></svg>',
    "target": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>',
    "search": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "calc": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="11" x2="8" y2="11"/><line x1="12" y1="11" x2="12" y2="11"/><line x1="16" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="8" y2="15"/><line x1="12" y1="15" x2="12" y2="15"/><line x1="16" y1="15" x2="16" y2="15"/></svg>',
    "pen": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    "chat": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "table": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
    "pdf": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15h6"/></svg>',
    "letter": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22 6 12 13 2 6"/></svg>',
    "check": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "folder": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "upload": '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
}

# ----------------------------------------------------------------------
# HTML building blocks
# ----------------------------------------------------------------------


def nav_html(active: str) -> str:
    links = []
    for href, label in NAV_ITEMS:
        cls = ' class="active" aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{cls}>{label}</a>')
    return (
        '<nav class="topnav"><div class="container nav-inner">'
        '<a class="brand" href="/">Nexo<span>ra</span></a>'
        '<input type="checkbox" id="navtoggle" class="navtoggle" aria-label="Menu">'
        '<label for="navtoggle" class="burger" aria-hidden="true">'
        "<span></span><span></span><span></span></label>"
        f'<div class="navlinks">{"".join(links)}</div>'
        "</div></nav>"
    )


def footer_html() -> str:
    return (
        '<footer class="footer"><div class="container row">'
        '<a class="brand" href="/">Nexo<span>ra</span></a>'
        "<span>AI-powered productivity tools for documents, HR &amp; careers.</span>"
        '<span style="margin-left:auto">&copy; 2026 Nexora</span>'
        "</div></footer>"
    )


def page(title: str, description: str, active: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - Nexora</title>
<meta name="description" content="{description}">
<style>{CSS}</style>
</head>
<body>
{nav_html(active)}
<main>
{body}
</main>
{footer_html()}
</body>
</html>"""


def card(icon: str, title: str, text: str, badge: str = "", extra: str = "") -> str:
    badge_html = f'<span class="tag {badge.lower()}">{badge}</span>' if badge else ""
    return (
        '<div class="card">'
        f'<div class="card-icon">{ICONS.get(icon, ICONS["doc"])}</div>'
        f"<h3>{title}</h3><p>{text}</p>{badge_html}{extra}</div>"
    )


def linked_card(href: str, icon: str, title: str, text: str, cta: str, badge: str = "") -> str:
    badge_html = f'<span class="tag {badge.lower()}">{badge}</span>' if badge else ""
    return (
        f'<a class="card card-link" href="{href}">'
        f'<div class="card-icon">{ICONS.get(icon, ICONS["doc"])}</div>'
        f"<h3>{title}</h3><p>{text}</p>"
        f'{badge_html}<p style="margin-top:12px"><strong style="color:var(--accent)">{cta} &rarr;</strong></p>'
        "</a>"
    )

# ----------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------


def home_page() -> str:
    body = f"""
<section class="hero"><div class="container">
  <p class="kicker">AI-powered productivity tools</p>
  <h1>Document, HR &amp; career work - done in minutes</h1>
  <p class="lede">Understand your documents, build stronger resumes and job
  descriptions, and handle everyday office paperwork without complicated software.</p>
</div></section>

<section class="section"><div class="container">
  <div class="grid">
    {linked_card("/document-ai", "doc", "Document AI Intelligence",
                 "Understand, analyze and work with your documents - summaries, answers and extracted data.",
                 "Open Document AI", badge="Live")}
    {linked_card("/hr-career", "briefcase", "HR &amp; Career Intelligence",
                 "Build better resumes, job descriptions and career documents with practical AI help.",
                 "Open HR &amp; Career")}
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head center">
    <h2>Featured products</h2>
    <p>Our most useful tools for job seekers and hiring teams.</p>
  </div>
  <div class="grid four">
    {linked_card("/resume-builder", "resume", "Resume Builder",
                 "Create a clean, professional resume that is easy for recruiters and software to read.",
                 "Explore", badge="Featured")}
    {card("target", "ATS Optimizer",
          "Check how well a resume passes applicant tracking systems and fix what holds it back.",
          badge="Soon")}
    {linked_card("/jd-builder", "pen", "JD Builder",
                 "Write clear, complete job descriptions that attract the right candidates.",
                 "Explore", badge="Featured")}
    {card("check", "Recruitment Optimizer",
          "Improve job ads and screening so good candidates stop slipping through.",
          badge="Soon")}
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head center">
    <h2>More tools, free to use</h2>
    <p>Simple utilities that solve everyday document and HR problems.</p>
  </div>
  <div class="grid four">
    {linked_card("/document-ai", "doc", "Document Summarizer", "Turn long documents into short, clear summaries.", "Use it", badge="Live")}
    {linked_card("/document-ai", "chat", "Document Q&amp;A", "Ask questions and get answers straight from your files.", "Use it", badge="Live")}
    {linked_card("/document-ai", "table", "Data Extraction", "Pull key fields and tables out of documents into Excel.", "Use it", badge="Live")}
    {card("calc", "CTC Calculator", "Break any CTC into take-home, deductions and benefits.", badge="Soon")}
    {card("calc", "Salary Calculator", "Estimate in-hand salary from any offer.", badge="Soon")}
    {card("calc", "Increment Calculator", "See what your next hike really means per month.", badge="Soon")}
    {card("calc", "Gratuity Calculator", "Work out gratuity on exit, instantly.", badge="Soon")}
    {card("letter", "HR Templates", "Offer, appointment, relieving letters and more - ready to use.", badge="Soon")}
  </div>
</div></section>
"""
    return page(
        "AI-powered productivity tools",
        "Nexora: AI-powered productivity tools for documents, HR and careers. "
        "Document AI, Resume Builder, JD Builder and free HR utilities.",
        "/",
        body,
    )


DOCUMENT_AI_BODY = r"""
<section class="page-hero"><div class="container">
  <span class="tag live">Live</span>
  <h1 style="margin-top:12px">Document AI Intelligence</h1>
  <p>Upload a document and let AI summarize it, answer your questions,
  extract the data inside and analyze it in depth.</p>
</div></section>

<section class="section"><div class="container">

  <div id="uploadCard">
    <div class="dropzone" id="dropzone" role="button" tabindex="0"
         aria-label="Upload a document">
      <span style="color:var(--accent)">__UPLOAD_ICON__</span>
      <h3>Drop your document here, or tap to choose</h3>
      <p>PDF, Word, TXT, CSV, Excel, or an image (PNG / JPG / WEBP). Max 12 MB.</p>
      <div class="filetypes">Your document is processed in memory for this
      session only. Upload only documents you are authorized to process.</div>
    </div>
    <input type="file" id="fileInput" hidden
           accept=".pdf,.docx,.txt,.csv,.xlsx,.xls,.png,.jpg,.jpeg,.webp">
    <div class="err" id="uploadErr"></div>
    <div id="aiOff" class="ai-off" style="display:none">
      The AI engine is being configured on the server. Uploads will start
      working shortly - please check back in a little while.
    </div>
  </div>

  <div class="workspace" id="workspace">
    <div class="docbar">
      <span class="card-icon" style="margin:0">__DOC_ICON__</span>
      <div>
        <div class="name" id="docName"></div>
        <div class="meta" id="docMeta"></div>
      </div>
      <span class="spacer"></span>
      <button class="btn ghost" id="newDocBtn" type="button">New document</button>
    </div>

    <div class="tabs" role="tablist">
      <button class="active" data-pane="summary" type="button">Summary</button>
      <button data-pane="chat" type="button">Chat</button>
      <button data-pane="extract" type="button">Extract data</button>
      <button data-pane="analyze" type="button">Analyze</button>
    </div>

    <div class="pane on" id="pane-summary">
      <p style="color:var(--muted);margin:0 0 4px">A clear, structured summary
      of the whole document - key points, important figures and takeaways.</p>
      <button class="btn" id="runSummary" type="button">Summarize document</button>
      <div class="err" id="errSummary"></div>
      <div class="result" id="outSummary"></div>
    </div>

    <div class="pane" id="pane-chat">
      <p style="color:var(--muted);margin:0">Ask anything about this document.
      Answers come only from its contents.</p>
      <div class="sugg" id="sugg"></div>
      <div class="chatlog" id="chatlog"></div>
      <div class="chatrow">
        <input id="chatInput" type="text" placeholder="Ask a question about the document..."
               autocomplete="off">
        <button class="btn" id="chatSend" type="button">Ask</button>
      </div>
      <div class="err" id="errChat"></div>
    </div>

    <div class="pane" id="pane-extract">
      <p style="color:var(--muted);margin:0 0 4px">Pull the key information out
      of the document as structured data, then download it as Excel.</p>
      <button class="btn" id="runExtract" type="button">Extract data</button>
      <a class="btn ghost" id="dlExcel" style="display:none;margin-left:8px"
         href="#">Download Excel</a>
      <div class="err" id="errExtract"></div>
      <div id="outExtract"></div>
    </div>

    <div class="pane" id="pane-analyze">
      <p style="color:var(--muted);margin:0 0 4px">Deep analysis: what this
      document is, strengths and weaknesses, risks, and anything important
      that is missing.</p>
      <button class="btn" id="runAnalyze" type="button">Analyze document</button>
      <div class="err" id="errAnalyze"></div>
      <div class="result" id="outAnalyze"></div>
    </div>
  </div>

</div></section>

<script>
(function () {
  var docId = null;
  var chatHistory = [];

  var dz = document.getElementById('dropzone');
  var fi = document.getElementById('fileInput');
  var upErr = document.getElementById('uploadErr');

  fetch('/api/config').then(function (r) { return r.json(); }).then(function (c) {
    if (!c.ai_ready) {
      document.getElementById('aiOff').style.display = 'block';
    }
  }).catch(function () {});

  dz.addEventListener('click', function () { fi.click(); });
  dz.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fi.click(); }
  });
  dz.addEventListener('dragover', function (e) {
    e.preventDefault(); dz.classList.add('drag');
  });
  dz.addEventListener('dragleave', function () { dz.classList.remove('drag'); });
  dz.addEventListener('drop', function (e) {
    e.preventDefault(); dz.classList.remove('drag');
    if (e.dataTransfer.files.length) { upload(e.dataTransfer.files[0]); }
  });
  fi.addEventListener('change', function () {
    if (fi.files.length) { upload(fi.files[0]); }
  });

  function upload(file) {
    upErr.textContent = '';
    if (file.size > 12 * 1024 * 1024) {
      upErr.textContent = 'That file is larger than 12 MB. Please use a smaller file.';
      return;
    }
    dz.innerHTML = '<h3><span class="spin"></span> Reading your document...</h3>' +
      '<p>' + escapeHtml(file.name) + '</p>';
    var fd = new FormData();
    fd.append('file', file);
    fetch('/api/documents', { method: 'POST', body: fd })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (!res.ok) { throw new Error(res.j.error || 'Upload failed.'); }
        openWorkspace(res.j);
      })
      .catch(function (e) {
        restoreDropzone();
        upErr.textContent = e.message || 'Upload failed. Please try another file.';
      });
  }

  function restoreDropzone() {
    dz.innerHTML = '<span style="color:var(--accent)">__UPLOAD_ICON__</span>' +
      '<h3>Drop your document here, or tap to choose</h3>' +
      '<p>PDF, Word, TXT, CSV, Excel, or an image (PNG / JPG / WEBP). Max 12 MB.</p>' +
      '<div class="filetypes">Your document is processed in memory for this ' +
      'session only. Upload only documents you are authorized to process.</div>';
  }

  function openWorkspace(info) {
    docId = info.doc_id;
    chatHistory = [];
    document.getElementById('docName').textContent = info.name;
    document.getElementById('docMeta').textContent = info.meta;
    document.getElementById('uploadCard').style.display = 'none';
    document.getElementById('workspace').classList.add('on');
    ['Summary', 'Chat', 'Extract', 'Analyze'].forEach(function (n) {
      var out = document.getElementById('out' + n);
      if (out) { out.innerHTML = ''; }
      var err = document.getElementById('err' + n);
      if (err) { err.textContent = ''; }
    });
    document.getElementById('chatlog').innerHTML = '';
    document.getElementById('dlExcel').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  document.getElementById('newDocBtn').addEventListener('click', function () {
    docId = null;
    document.getElementById('workspace').classList.remove('on');
    document.getElementById('uploadCard').style.display = 'block';
    restoreDropzone();
    fi.value = '';
  });

  var tabs = document.querySelectorAll('.tabs button');
  tabs.forEach(function (b) {
    b.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      document.querySelectorAll('.pane').forEach(function (p) { p.classList.remove('on'); });
      document.getElementById('pane-' + b.dataset.pane).classList.add('on');
    });
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function renderMarkdownLite(el, text) {
    var html = escapeHtml(text);
    html = html.replace(/^#### (.*)$/gm, '<h4>$1</h4>');
    html = html.replace(/^### (.*)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.*)$/gm, '<h4>$1</h4>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/^\s*[-*] (.*)$/gm, '\u2022 $1');
    el.innerHTML = html;
  }

  function aiCall(url, payload, btn, errEl, onDone) {
    errEl.textContent = '';
    var old = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="spin"></span> Working...';
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload || {})
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        btn.disabled = false; btn.textContent = old;
        if (!res.ok) { errEl.textContent = res.j.error || 'Something went wrong.'; return; }
        onDone(res.j);
      })
      .catch(function () {
        btn.disabled = false; btn.textContent = old;
        errEl.textContent = 'Network problem. Please try again.';
      });
  }

  document.getElementById('runSummary').addEventListener('click', function () {
    var btn = this;
    aiCall('/api/documents/' + docId + '/summary', {}, btn,
      document.getElementById('errSummary'), function (j) {
        renderMarkdownLite(document.getElementById('outSummary'), j.summary);
      });
  });

  var suggestions = [
    'What are the important points?',
    'What are the key figures or amounts?',
    'What action items or deadlines are mentioned?',
    'Explain this document in simple words'
  ];
  var suggBox = document.getElementById('sugg');
  suggestions.forEach(function (s) {
    var b = document.createElement('button');
    b.type = 'button'; b.textContent = s;
    b.addEventListener('click', function () { askChat(s); });
    suggBox.appendChild(b);
  });

  var chatInput = document.getElementById('chatInput');
  var chatSend = document.getElementById('chatSend');
  chatSend.addEventListener('click', function () { askChat(chatInput.value); });
  chatInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { askChat(chatInput.value); }
  });

  function addMsg(cls, text) {
    var d = document.createElement('div');
    d.className = 'msg ' + cls;
    renderMarkdownLite(d, text);
    document.getElementById('chatlog').appendChild(d);
    d.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    return d;
  }

  function askChat(q) {
    q = (q || '').trim();
    if (!q || !docId) { return; }
    chatInput.value = '';
    addMsg('user', q);
    var thinking = addMsg('ai', '...');
    chatSend.disabled = true;
    fetch('/api/documents/' + docId + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: q, history: chatHistory.slice(-10) })
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        chatSend.disabled = false;
        if (!res.ok) { renderMarkdownLite(thinking, res.j.error || 'Something went wrong.'); return; }
        renderMarkdownLite(thinking, res.j.answer);
        chatHistory.push({ role: 'user', text: q });
        chatHistory.push({ role: 'assistant', text: res.j.answer });
      })
      .catch(function () {
        chatSend.disabled = false;
        renderMarkdownLite(thinking, 'Network problem. Please try again.');
      });
  }

  document.getElementById('runExtract').addEventListener('click', function () {
    var btn = this;
    aiCall('/api/documents/' + docId + '/extract', {}, btn,
      document.getElementById('errExtract'), function (j) {
        var box = document.getElementById('outExtract');
        var html = '';
        var fields = j.fields || {};
        var keys = Object.keys(fields);
        if (keys.length) {
          html += '<table class="kv"><tr><th>Field</th><th>Value</th></tr>';
          keys.forEach(function (k) {
            html += '<tr><td>' + escapeHtml(k) + '</td><td>' + escapeHtml(fields[k]) + '</td></tr>';
          });
          html += '</table>';
        }
        (j.tables || []).forEach(function (t) {
          html += '<h4 style="margin:18px 0 6px">' + escapeHtml(t.name || 'Table') + '</h4>';
          html += '<table class="kv">';
          (t.rows || []).forEach(function (row, i) {
            html += '<tr>';
            row.forEach(function (cell) {
              html += i === 0 ? '<th>' + escapeHtml(cell) + '</th>'
                              : '<td>' + escapeHtml(cell) + '</td>';
            });
            html += '</tr>';
          });
          html += '</table>';
        });
        if (!html) { html = '<div class="result">No structured data found in this document.</div>'; }
        box.innerHTML = html;
        var dl = document.getElementById('dlExcel');
        dl.href = '/api/documents/' + docId + '/export.xlsx';
        dl.style.display = 'inline-block';
      });
  });

  document.getElementById('runAnalyze').addEventListener('click', function () {
    var btn = this;
    aiCall('/api/documents/' + docId + '/analyze', {}, btn,
      document.getElementById('errAnalyze'), function (j) {
        renderMarkdownLite(document.getElementById('outAnalyze'), j.analysis);
      });
  });
})();
</script>
"""


def document_ai_page() -> str:
    body = DOCUMENT_AI_BODY.replace("__UPLOAD_ICON__", ICONS["upload"]).replace(
        "__DOC_ICON__", ICONS["doc"]
    )
    return page(
        "Document AI",
        "Document AI: upload a document and let AI summarize it, answer questions, extract data to Excel and analyze it.",
        "/document-ai",
        body,
    )


# ----------------------------------------------------------------------
# Phase 3: HR & Career - Career AI tools
# ----------------------------------------------------------------------

CAREER_SLUGS = [
    "resume-builder", "resume-analyzer", "ats-optimizer", "jd-builder",
    "jd-analyzer", "recruitment-optimizer", "cover-letter-builder",
    "offer-letter-analyzer",
]

CAREER_TOOLS = {
    "resume-builder": {
        "title": "Resume Builder",
        "icon": "resume",
        "tagline": "Answer a few questions and get a complete, ATS-friendly professional resume.",
        "card": "A complete, ATS-friendly resume written from your details.",
        "seo": "Build a professional ATS-friendly resume in minutes with AI.",
        "source": None,
        "button": "Build my resume",
        "fields": [
            ["name", "Full name", "e.g. Priya Sharma", "input"],
            ["role", "Job you are applying for", "e.g. Digital Marketing Executive", "input"],
            ["experience", "Experience so far", "e.g. 3 years as Marketing Associate at ABC Ltd, handled SEO and ad campaigns", "textarea"],
            ["skills", "Key skills", "e.g. SEO, Google Ads, content writing, Canva", "textarea"],
            ["achievements", "Achievements / projects (with numbers if possible)", "e.g. Grew organic traffic 120% in 8 months; managed Rs. 5L/month ad budget", "textarea"],
            ["education", "Education", "e.g. B.Com, Delhi University, 2021", "input"],
        ],
        "required": ["name", "role"],
        "prompt": (
            "Write a complete, professional, ATS-friendly resume for {name}, "
            "targeting the role of {role}.\n\nDetails provided:\n"
            "- Experience: {experience}\n- Skills: {skills}\n"
            "- Achievements: {achievements}\n- Education: {education}\n\n"
            "Rules: use ## headings (Summary, Skills, Experience, Achievements, "
            "Education), strong action verbs, quantify results where the details "
            "allow, and never invent employers, degrees or numbers - if a detail "
            "is missing, keep that part short. Simple formatting an ATS can parse."
        ),
        "download": True,
    },
    "resume-analyzer": {
        "title": "Resume Analyzer",
        "icon": "search",
        "tagline": "An honest, expert review of your resume - score, weaknesses and fixes.",
        "card": "Score, weaknesses, missing keywords and concrete fixes.",
        "seo": "Free AI resume analysis: ATS check, weaknesses, missing keywords and fixes.",
        "source": {"label": "Your resume", "help": "Paste your resume text, or upload the file (PDF, DOCX, TXT)."},
        "button": "Analyze my resume",
        "fields": [
            ["role", "Target role (optional)", "e.g. HR Executive - helps focus the review", "input"],
        ],
        "required": [],
        "prompt": (
            "You are an expert resume reviewer and hiring manager. Analyze this "
            "resume honestly and practically. Target role: {role}. Use ## "
            "headings and bullets. Cover: 1) Overall verdict with a score out of "
            "100, 2) ATS assessment - will screening software parse and rank this "
            "well?, 3) Missing skills and keywords for the target role (infer "
            "the role from the resume if not given), 4) Weak wording - quote the "
            "vague lines, 5) Experience problems - gaps, unclear impact, missing "
            "numbers, 6) Formatting issues, 7) Summary/profile problems, 8) Top 5 "
            "fixes in priority order. Base everything only on the resume - no "
            "invented facts."
        ),
        "download": False,
    },
    "ats-optimizer": {
        "title": "ATS Optimizer",
        "icon": "target",
        "tagline": "Match your resume to a job description and beat the screening software.",
        "card": "Match score, missing keywords and tailoring advice for a specific job.",
        "seo": "Optimize your resume for applicant tracking systems against a specific job description.",
        "source": {"label": "Your resume", "help": "Paste your resume text, or upload the file (PDF, DOCX, TXT)."},
        "button": "Check my ATS match",
        "fields": [
            ["jd", "Job description you are applying to", "Paste the full job description here", "textarea"],
        ],
        "required": ["jd"],
        "prompt": (
            "Compare this resume against this job description as an ATS (applicant "
            "tracking system) would.\n\nJob description:\n{jd}\n\nUse ## headings "
            "and bullets. Give: 1) ATS match score out of 100, 2) Keywords from "
            "the JD missing in the resume (list them), 3) Keywords already "
            "present, 4) Section-by-section tailoring advice, 5) A rewritten "
            "summary line matched to this JD, 6) Bullet points to add or rewrite, "
            "7) Final checklist before applying. Be specific and honest."
        ),
        "download": False,
    },
    "jd-builder": {
        "title": "JD Builder",
        "icon": "pen",
        "tagline": "A complete, clear job description written in minutes.",
        "card": "Complete job descriptions with the right structure and tone.",
        "seo": "Write clear, complete job descriptions in minutes with AI.",
        "source": None,
        "button": "Write the JD",
        "fields": [
            ["role", "Job title", "e.g. Customer Support Executive", "input"],
            ["company", "Company name", "e.g. Nexora Technologies", "input"],
            ["seniority", "Level", "e.g. Fresher / 2-4 years / Senior", "input"],
            ["location", "Location", "e.g. Bangalore (hybrid)", "input"],
            ["musthave", "Must-have skills", "e.g. fluent English, Excel, CRM tools", "textarea"],
            ["nicetohave", "Good to have (optional)", "e.g. experience in e-commerce", "input"],
            ["salary", "Salary range (optional)", "e.g. Rs. 3-4.5 LPA", "input"],
        ],
        "required": ["role", "company"],
        "prompt": (
            "Write a complete, professional job description for {role} at "
            "{company}. Level: {seniority}. Location: {location}. Must-have "
            "skills: {musthave}. Good to have: {nicetohave}. Salary: {salary}.\n\n"
            "Use ## headings: About the role, Responsibilities, Must-have "
            "requirements, Good to have, What we offer, How to apply. Use "
            "inclusive, plain language, realistic requirements (no impossible "
            "wish lists), and no jargon. Omit the salary line if not provided."
        ),
        "download": True,
    },
    "jd-analyzer": {
        "title": "JD Analyzer",
        "icon": "search",
        "tagline": "Check a job description for gaps, vague wording and biased language.",
        "card": "Find gaps, bias and clarity issues before you post a JD.",
        "seo": "Analyze a job description for completeness, clarity and inclusive language.",
        "source": {"label": "The job description", "help": "Paste the JD text, or upload the file."},
        "button": "Analyze this JD",
        "fields": [],
        "required": [],
        "prompt": (
            "Analyze this job description as an expert recruiter. Use ## headings "
            "and bullets. Cover: 1) Overall score out of 100, 2) Missing sections "
            "candidates expect (salary, location, benefits, process), 3) Vague or "
            "buzzword-heavy lines - quote them, 4) Biased or exclusionary "
            "language, 5) Unrealistic requirement pile-ups, 6) Clarity of the "
            "responsibilities, 7) Rewrites for the weakest 5 lines. Be specific "
            "and practical."
        ),
        "download": False,
    },
    "recruitment-optimizer": {
        "title": "Recruitment Optimizer",
        "icon": "check",
        "tagline": "A practical hiring plan: better job ads, screening questions, faster process.",
        "card": "Sourcing channels, screening questions and a faster hiring process.",
        "seo": "Improve your hiring: job ad fixes, sourcing channels, screening questions and process.",
        "source": {"label": "Your current job ad (optional)", "help": "Paste the job ad text, or upload the file. Optional but improves the advice."},
        "button": "Optimize my hiring",
        "fields": [
            ["role", "Role you are hiring for", "e.g. Field Sales Executive", "input"],
            ["problem", "Biggest hiring problem right now", "e.g. lots of applications but few good candidates / offer dropouts", "textarea"],
        ],
        "required": ["role"],
        "prompt": (
            "Act as a senior talent acquisition consultant in India. Role being "
            "hired: {role}. Current problem: {problem}.\n\nIf a job ad is "
            "attached, critique it first. Use ## headings and bullets. Give a "
            "practical plan: 1) Job ad improvements, 2) Best sourcing channels "
            "for this role in India, 3) 8 screening questions with what good "
            "answers look like, 4) A fast interview process (stages, owners, "
            "timelines), 5) Offer and joining tips that reduce dropouts. Be "
            "specific and realistic for the Indian market."
        ),
        "download": False,
    },
    "cover-letter-builder": {
        "title": "Cover Letter Builder",
        "icon": "letter",
        "tagline": "A tailored cover letter matched to the job - no cliches.",
        "card": "Tailored cover letters that match your resume to the job.",
        "seo": "Write a tailored cover letter matched to the job description with AI.",
        "source": {"label": "Your resume", "help": "Paste your resume text, or upload the file."},
        "button": "Write my cover letter",
        "fields": [
            ["jd", "Job description or role you are applying to", "Paste the job description (or at least the role and company)", "textarea"],
        ],
        "required": ["jd"],
        "prompt": (
            "Write a tailored cover letter of 250-350 words for this candidate "
            "applying to:\n\n{jd}\n\nMatch the candidate's real experience from "
            "the resume to what the role asks for. Professional but human tone, "
            "no cliches like 'I am writing to express my interest', no invented "
            "facts. Output the letter only - no commentary."
        ),
        "download": True,
    },
    "offer-letter-analyzer": {
        "title": "Offer Letter Analyzer",
        "icon": "doc",
        "tagline": "Understand every clause of an offer before you sign.",
        "card": "Clause-by-clause explanation, red flags and negotiation points.",
        "seo": "Understand your offer letter: CTC breakdown, clauses, red flags and negotiation tips.",
        "source": {"label": "The offer letter", "help": "Paste the offer letter text, or upload the file."},
        "button": "Analyze this offer",
        "fields": [],
        "required": [],
        "prompt": (
            "Explain this offer letter for a job seeker in India, clause by "
            "clause. Use ## headings and bullets. Cover: 1) Compensation - CTC "
            "vs realistic take-home, variable pay catches, 2) Benefits and what "
            "they are really worth, 3) Clauses to watch - bond or service "
            "agreement, notice period, non-compete, probation, termination "
            "terms, 4) What is missing (joining bonus terms, relocation, "
            "insurance, leave), 5) Red flags, 6) Fair negotiation points with "
            "suggested wording. Plain English, no legal jargon. Add a final note "
            "that this is guidance, not legal advice."
        ),
        "download": False,
    },
}

CAREER_BODY = """
<section class="page-hero"><div class="container">
  <span class="tag live">Live</span>
  <h1 style="margin-top:12px">__TITLE__</h1>
  <p>__TAGLINE__</p>
</div></section>
<section class="section"><div class="container">
  <div class="card" style="max-width:780px">
    <div id="srcBlock"></div>
    <div id="formFields"></div>
    <div class="toolbar">
      <button class="btn" id="goBtn" onclick="runTool()">__BUTTON__</button>
      <span id="spin" class="spin" style="display:none"></span>
      <span class="hint" id="wait" style="display:none">AI is working - this can take up to a minute.</span>
    </div>
    <div class="err" id="err"></div>
  </div>
  <div class="result card" id="resultBox" style="max-width:780px;display:none">
    <div id="result"></div>
    <div class="toolbar" id="dlBar" style="display:none">
      <button class="btn ghost" onclick="downloadDocx()">Download as Word (.docx)</button>
    </div>
  </div>
  <div class="note" style="max-width:780px">AI-generated output - review it
  before using it for real applications or hiring.</div>
</div></section>
<input type="file" id="fileInput" hidden
  accept=".pdf,.docx,.txt,.md,.csv,.xlsx,.xls,image/*">
<script>
var CFG = __CFG_JSON__;
var state = {docId: null, lastResult: ""};
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function mdRender(md) {
  var lines = String(md).split("\\n"), html = "", inList = false;
  function closeList() { if (inList) { html += "</ul>"; inList = false; } }
  function inline(x) { return esc(x).replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>"); }
  for (var i = 0; i < lines.length; i++) {
    var t = lines[i].replace(/^\\s+|\\s+$/g, "");
    if (!t) { closeList(); continue; }
    if (t.indexOf("## ") === 0) { closeList(); html += "<h4>" + inline(t.slice(3)) + "</h4>"; }
    else if (t.indexOf("# ") === 0) { closeList(); html += "<h4>" + inline(t.slice(2)) + "</h4>"; }
    else if (/^[-*] /.test(t)) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += "<li>" + inline(t.slice(2)) + "</li>";
    } else { closeList(); html += "<p>" + inline(t) + "</p>"; }
  }
  closeList();
  return html;
}
function buildForm() {
  var h = "";
  if (CFG.source) {
    h += '<div class="srcbox"><div class="field"><label>' + esc(CFG.source.label) + '</label>'
      + '<textarea id="srcText" placeholder="Paste the text here..."></textarea>'
      + '<div class="hint">' + esc(CFG.source.help) + '</div></div>'
      + '<div class="toolbar" style="margin-top:4px">'
      + '<button class="btn ghost" type="button" onclick="document.getElementById(\\'fileInput\\').click()">Upload file instead</button>'
      + '<span class="attached" id="attName"></span></div></div>';
  }
  CFG.fields.forEach(function (f) {
    h += '<div class="field"><label for="f_' + f[0] + '">' + esc(f[1]) + '</label>';
    if (f[3] === "textarea") {
      h += '<textarea id="f_' + f[0] + '" placeholder="' + esc(f[2]) + '"></textarea>';
    } else {
      h += '<input id="f_' + f[0] + '" type="text" placeholder="' + esc(f[2]) + '">';
    }
    h += '</div>';
  });
  document.getElementById("formFields").innerHTML = h;
  document.getElementById("srcBlock").innerHTML = "";
  if (CFG.source) {
    var sb = document.getElementById("formFields").innerHTML;
  }
}
buildForm();
var fi = document.getElementById("fileInput");
fi.onchange = function () {
  if (!fi.files.length) return;
  var fd = new FormData();
  fd.append("file", fi.files[0]);
  var att = document.getElementById("attName");
  att.textContent = "Uploading...";
  fetch("/api/documents", {method: "POST", body: fd}).then(function (r) {
    return r.json().then(function (j) { return {ok: r.ok, j: j}; });
  }).then(function (o) {
    if (o.ok && o.j.doc_id) {
      state.docId = o.j.doc_id;
      att.textContent = "Attached: " + o.j.name + " (" + o.j.meta + ")";
    } else {
      att.textContent = "";
      showErr(o.j.error || "Could not upload that file.");
    }
  }).catch(function () { att.textContent = ""; showErr("Upload failed. Please try again."); });
};
function showErr(m) { document.getElementById("err").textContent = m; }
function runTool() {
  showErr("");
  var fields = {};
  CFG.fields.forEach(function (f) {
    fields[f[0]] = document.getElementById("f_" + f[0]).value.trim();
  });
  var sourceText = CFG.source && document.getElementById("srcText")
    ? document.getElementById("srcText").value.trim() : "";
  if (!state.docId && CFG.source && !sourceText && CFG.sourceRequired) {
    showErr("Please paste or upload " + CFG.source.label.toLowerCase() + ".");
    return;
  }
  var btn = document.getElementById("goBtn");
  btn.disabled = true;
  document.getElementById("spin").style.display = "inline-block";
  document.getElementById("wait").style.display = "inline";
  fetch("/api/career/" + CFG.slug, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({fields: fields, doc_id: state.docId, source_text: sourceText})
  }).then(function (r) {
    return r.json().then(function (j) { return {ok: r.ok, j: j}; });
  }).then(function (o) {
    btn.disabled = false;
    document.getElementById("spin").style.display = "none";
    document.getElementById("wait").style.display = "none";
    if (o.ok && o.j.result) {
      state.lastResult = o.j.result;
      document.getElementById("result").innerHTML = mdRender(o.j.result);
      document.getElementById("resultBox").style.display = "block";
      document.getElementById("dlBar").style.display = CFG.download ? "flex" : "none";
      document.getElementById("resultBox").scrollIntoView({behavior: "smooth"});
    } else {
      showErr(o.j.error || "Something went wrong. Please try again.");
    }
  }).catch(function () {
    btn.disabled = false;
    document.getElementById("spin").style.display = "none";
    document.getElementById("wait").style.display = "none";
    showErr("Network error. Please try again.");
  });
}
function downloadDocx() {
  if (!state.lastResult) return;
  fetch("/api/download-docx", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title: CFG.title, content: state.lastResult})
  }).then(function (r) {
    if (!r.ok) { showErr("Could not create the Word file. Please try again."); return null; }
    return r.blob();
  }).then(function (blob) {
    if (!blob) return;
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = CFG.slug + ".docx";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 800);
  });
}
</script>
"""


def career_tool_page(slug: str) -> str:
    spec = CAREER_TOOLS[slug]
    cfg = {
        "slug": slug,
        "title": spec["title"],
        "fields": spec["fields"],
        "source": spec.get("source"),
        "sourceRequired": bool(spec.get("source")) and slug not in ("recruitment-optimizer",),
        "download": bool(spec.get("download")),
    }
    body = (CAREER_BODY
            .replace("__CFG_JSON__", json.dumps(cfg))
            .replace("__TITLE__", spec["title"])
            .replace("__TAGLINE__", spec["tagline"])
            .replace("__BUTTON__", spec["button"]))
    return page(spec["title"], spec["seo"], "/hr-career", body)


def hr_career_page() -> str:
    tools = "".join(
        linked_card(f"/career/{slug}", spec["icon"], spec["title"],
                    spec["card"], "Use it", badge="Live")
        for slug, spec in CAREER_TOOLS.items()
    )
    docs = "".join(
        f'<span class="tag">{name}</span>' for name in (
            "Offer Letter", "Appointment Letter", "Salary Increment Letter",
            "Promotion Letter", "Experience Certificate", "Relieving Letter",
            "Warning Letter", "Exit Interview Form")
    )
    body = f"""
<section class="page-hero"><div class="container">
  <h1>HR &amp; Career Intelligence</h1>
  <p>Practical AI tools for job seekers and HR teams - resumes, job
  descriptions, letters, documents and calculators.</p>
</div></section>
<section class="section"><div class="container">
  <h2 class="sech">Career AI</h2>
  <div class="grid three">{tools}</div>

  <h2 class="sech">HR Utilities</h2>
  <div class="grid three">
    {linked_card("/hr/calculators", "calc", "HR Calculators",
                 "CTC breakdown, take-home pay, increment, gratuity and notice period - instant, no sign-up.",
                 "Open calculators", badge="Live")}
  </div>

  <h2 class="sech">HR Documents</h2>
  <div class="grid three">
    {linked_card("/hr/documents", "letter", "HR Document Generator",
                 "Offer, appointment, increment, promotion, experience, relieving, warning and exit forms - ready to download as Word files.",
                 "Create documents", badge="Live")}
  </div>
  <p style="margin-top:12px">{docs}</p>
</div></section>
"""
    return page("HR & Career", "HR and career AI tools: resume builder, resume analyzer, ATS optimizer, JD builder, cover letters, offer analysis, HR calculators and HR documents.", "/hr-career", body)


# ----------------------------------------------------------------------
# Phase 3: HR calculators (client-side, instant)
# ----------------------------------------------------------------------

CALC_BODY = """
<section class="page-hero"><div class="container">
  <span class="tag live">Live</span>
  <h1 style="margin-top:12px">HR Calculators</h1>
  <p>Instant answers for the most common Indian salary questions. No sign-up,
  nothing stored - everything runs in your browser.</p>
</div></section>
<section class="section"><div class="container" style="max-width:780px">
  <div class="pill-tabs" id="tabs"></div>
  <div class="card">
    <div id="calcForm"></div>
    <div class="toolbar"><button class="btn" onclick="runCalc()">Calculate</button></div>
    <div class="err" id="err"></div>
    <div id="calcOut"></div>
    <div class="hint" id="calcNote"></div>
  </div>
</div></section>
<script>
var CALCS = [
  {id: "ctc", name: "CTC Breakdown",
   desc: "See how an annual CTC typically splits into components.",
   fields: [["ctc", "Annual CTC (Rs.)", "e.g. 600000"]],
   note: "A common structure: Basic 40% of CTC, HRA 50% of Basic, employer PF 12% of Basic, gratuity 4.81% of Basic, rest as special allowance. Actual structures vary by company."},
  {id: "takehome", name: "Take-home Pay",
   desc: "Estimate monthly in-hand salary from CTC (new tax regime).",
   fields: [["ctc", "Annual CTC (Rs.)", "e.g. 600000"]],
   note: "Simplified estimate using the new regime (FY 2025-26) with Rs. 75,000 standard deduction, employee PF 12% of Basic (40% of CTC) and Rs. 200/month professional tax. Actual take-home depends on your company's structure and your tax choices."},
  {id: "increment", name: "Increment",
   desc: "New salary after a percentage hike.",
   fields: [["cur", "Current annual CTC (Rs.)", "e.g. 600000"], ["pct", "Hike (%)", "e.g. 12"]],
   note: ""},
  {id: "gratuity", name: "Gratuity",
   desc: "Gratuity payable under the Payment of Gratuity Act.",
   fields: [["basic", "Last drawn monthly Basic + DA (Rs.)", "e.g. 25000"], ["years", "Years of service", "e.g. 6"]],
   note: "Formula: 15/26 x last drawn Basic+DA x completed years (6+ months rounds up). Gratuity generally applies after 5 years of continuous service."},
  {id: "notice", name: "Notice Period",
   desc: "Find your last working day from your resignation date.",
   fields: [["date", "Resignation date", "", "date"], ["days", "Notice period (days)", "e.g. 30"]],
   note: "Counts calendar days. Check your offer/appointment letter - some companies count differently or allow buy-out."}
];
var cur = "ctc";
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function inr(n) {
  return "Rs. " + Math.round(n).toLocaleString("en-IN");
}
function buildTabs() {
  var h = "";
  CALCS.forEach(function (c) {
    h += '<button data-id="' + c.id + '"' + (c.id === cur ? ' class="active"' : '')
      + ' onclick="pick(\\'' + c.id + '\\')">' + c.name + '</button>';
  });
  document.getElementById("tabs").innerHTML = h;
}
function pick(id) { cur = id; buildTabs(); buildForm(); }
function buildForm() {
  var c = CALCS.find(function (x) { return x.id === cur; });
  var h = '<p class="hint" style="margin-bottom:14px">' + esc(c.desc) + '</p>';
  c.fields.forEach(function (f) {
    h += '<div class="field"><label>' + esc(f[1]) + '</label><input id="c_' + f[0]
      + '" type="' + (f[3] || "number") + '" placeholder="' + esc(f[2]) + '"></div>';
  });
  document.getElementById("calcForm").innerHTML = h;
  document.getElementById("calcOut").innerHTML = "";
  document.getElementById("calcNote").textContent = "";
  document.getElementById("err").textContent = "";
}
function num(id) {
  var v = parseFloat(document.getElementById(id).value);
  return isNaN(v) ? null : v;
}
function table(rows) {
  var h = '<table class="kv">';
  rows.forEach(function (r) { h += "<tr><th>" + r[0] + "</th><td>" + r[1] + "</td></tr>"; });
  return h + "</table>";
}
function runCalc() {
  var err = document.getElementById("err");
  err.textContent = "";
  var out = "", c = CALCS.find(function (x) { return x.id === cur; });
  document.getElementById("calcNote").textContent = c.note || "";
  if (cur === "ctc") {
    var ctc = num("c_ctc");
    if (!ctc || ctc <= 0) { err.textContent = "Enter a valid annual CTC."; return; }
    var basic = ctc * 0.40, hra = basic * 0.50, pf = basic * 0.12,
        grat = basic * 0.0481, spl = ctc - basic - hra - pf - grat;
    out = table([["Basic (40% of CTC)", inr(basic) + " / year - " + inr(basic / 12) + " / month"],
      ["HRA (50% of Basic)", inr(hra) + " / year"],
      ["Employer PF (12% of Basic)", inr(pf) + " / year"],
      ["Gratuity (4.81% of Basic)", inr(grat) + " / year"],
      ["Special allowance (balance)", inr(spl) + " / year"],
      ["Total CTC", inr(ctc) + " / year"]]);
  } else if (cur === "takehome") {
    var ctc2 = num("c_ctc");
    if (!ctc2 || ctc2 <= 0) { err.textContent = "Enter a valid annual CTC."; return; }
    var basic2 = ctc2 * 0.40, epf = basic2 * 0.12, ptax = 2400,
        taxable = Math.max(0, ctc2 - 75000), tax = 0, rem = taxable, lo = 0;
    var slabs = [[400000, 0], [400000, 0.05], [400000, 0.10], [400000, 0.15],
                 [400000, 0.20], [400000, 0.25], [Infinity, 0.30]];
    for (var i = 0; i < slabs.length; i++) {
      var w = Math.min(rem, slabs[i][0]);
      if (w <= 0) break;
      tax += w * slabs[i][1]; rem -= w;
    }
    if (taxable <= 1200000) tax = 0;
    tax = tax * 1.04;
    var monthly = (ctc2 - epf - ptax - tax) / 12;
    out = table([["Annual CTC", inr(ctc2)],
      ["Employee PF (approx)", "- " + inr(epf)],
      ["Professional tax", "- " + inr(ptax)],
      ["Income tax (new regime, incl. cess)", "- " + inr(tax)],
      ["Estimated monthly take-home", inr(monthly)]]);
  } else if (cur === "increment") {
    var curCtc = num("c_cur"), pct = num("c_pct");
    if (!curCtc || curCtc <= 0 || pct === null) { err.textContent = "Enter current CTC and hike %."; return; }
    var newCtc = curCtc * (1 + pct / 100);
    out = table([["Current CTC", inr(curCtc)],
      ["Hike", pct + "%"],
      ["New CTC", inr(newCtc)],
      ["Increase per year", inr(newCtc - curCtc)],
      ["Increase per month", inr((newCtc - curCtc) / 12)]]);
  } else if (cur === "gratuity") {
    var b = num("c_basic"), y = num("c_years");
    if (!b || b <= 0 || !y || y <= 0) { err.textContent = "Enter monthly Basic+DA and years of service."; return; }
    var yrs = Math.floor(y), frac = y - yrs;
    if (frac >= 0.5) yrs += 1;
    var g = 15 / 26 * b * yrs;
    out = table([["Last drawn Basic + DA", inr(b) + " / month"],
      ["Counted years of service", yrs + (frac >= 0.5 ? " (rounded up)" : "")],
      ["Gratuity payable", inr(g)]]);
    if (y < 4.5) out += '<p class="hint" style="color:var(--red)">Note: gratuity usually needs 5 years of continuous service.</p>';
  } else if (cur === "notice") {
    var d = document.getElementById("c_date").value, days = num("c_days");
    if (!d || !days || days <= 0) { err.textContent = "Pick a resignation date and notice days."; return; }
    var dt = new Date(d + "T00:00:00");
    dt.setDate(dt.getDate() + days);
    out = table([["Resignation date", new Date(d + "T00:00:00").toLocaleDateString("en-IN", {day: "numeric", month: "long", year: "numeric"})],
      ["Notice period", days + " days"],
      ["Last working day", dt.toLocaleDateString("en-IN", {weekday: "long", day: "numeric", month: "long", year: "numeric"})]]);
  }
  document.getElementById("calcOut").innerHTML = out;
}
buildTabs();
buildForm();
</script>
"""


def calculators_page() -> str:
    return page("HR Calculators",
                "Free HR calculators: CTC breakdown, take-home pay, increment, gratuity and notice period for India.",
                "/hr-career", CALC_BODY)


# ----------------------------------------------------------------------
# Phase 3: HR document generator
# ----------------------------------------------------------------------


class _F(dict):
    def __missing__(self, key):
        return "(not provided)"


def _today() -> str:
    return time.strftime("%d %B %Y")


def _doc_footer() -> str:
    return ("\n\n---\nGenerated with Nexora HR Document Generator on "
            + _today()
            + ". This is a template - have your HR or legal advisor review it before use.")


def _render_offer(f):
    return """{company}

Date: __DATE__

Dear {candidate},

## Offer of Employment

We are pleased to offer you the position of {role} at {company}.

- Designation: {role}
- Date of joining: {joining_date}
- Work location: {location}
- Annual CTC: Rs. {ctc}

A detailed compensation breakup and terms of employment will be provided in
your appointment letter. This offer is subject to satisfactory verification
of your documents and references.

Please sign and return a copy of this letter as your acceptance.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_appointment(f):
    return """{company}

Date: __DATE__

Dear {employee},

## Appointment Letter

We are delighted to confirm your appointment as {role} in the {department}
department at {company}, effective {joining_date}.

- Designation: {role}
- Department: {department}
- Work location: {location}
- Annual CTC: Rs. {ctc}
- Probation period: {probation}

Your employment will be governed by the company's policies, including
confidentiality, code of conduct and notice period terms shared separately.
During probation, either party may end the employment as per the notice
terms in company policy.

We look forward to your contribution.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_increment(f):
    return """{company}

Date: __DATE__

Dear {employee},

## Salary Increment Letter

In recognition of your performance and contribution as {role}, we are pleased
to revise your compensation as follows:

- Revised annual CTC: Rs. {new_ctc}
- Effective date: {effective_date}
- Increase: {hike}

All other terms of your employment remain unchanged. A revised compensation
breakup will be shared by HR.

Congratulations, and thank you for your work.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_promotion(f):
    return """{company}

Date: __DATE__

Dear {employee},

## Promotion Letter

We are pleased to announce your promotion from {old_role} to {new_role},
effective {effective_date}, at our {location} location.

This promotion recognizes your performance, commitment and the value you
bring to {company}. Your revised responsibilities and any compensation
changes will be communicated by HR separately.

Congratulations - we look forward to your continued success.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_experience(f):
    return """{company}

Date: __DATE__

## Experience Certificate

This is to certify that {employee} was employed with {company} as {role}
from {start_date} to {end_date}.

During this period, {employee} carried out their responsibilities
professionally and was found to be sincere and reliable. We wish them success
in their future endeavours.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_relieving(f):
    return """{company}

Date: __DATE__

Dear {employee},

## Relieving Letter

This is to confirm that your resignation from the position of {role} at
{company} has been accepted, and you are relieved of your duties effective
{last_day}.

Your full and final settlement will be processed as per company policy.
We thank you for your contribution and wish you the best.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_warning(f):
    return """{company}

Date: __DATE__

Dear {employee},

## Warning Letter

This letter concerns the following matter, observed on {incident_date}:

{issue}

This conduct is not in line with the expectations of your role as {role} and
company policy. You are expected to correct this immediately. Further
occurrence may lead to stricter disciplinary action, up to and including
termination.

You may share your explanation with HR within three working days of this
letter.

Sincerely,
{hr_name}
{company}""".format_map(_F(f)) + _doc_footer()


def _render_exit(f):
    return """{company}

## Exit Interview Form

- Employee: {employee}
- Role: {role}
- Last working day: {last_day}
- Reporting manager: {manager}
- Stated reason for leaving: {reason}

## Discussion points

- What prompted you to start looking for a new role?
- How was your relationship with your manager and team?
- What did you enjoy most about working here?
- What should we improve - processes, tools, culture, growth?
- Would you consider returning or referring others? Why / why not?

Interviewer notes:

____________________________________________________

____________________________________________________

Conducted by: {hr_name}          Date: __DATE__""".format_map(_F(f)) + _doc_footer()


HR_DOCS = {
    "offer-letter": {
        "title": "Offer Letter",
        "fields": [
            ["company", "Company name", "e.g. Nexora Technologies"],
            ["candidate", "Candidate name", "e.g. Priya Sharma"],
            ["role", "Job title", "e.g. Marketing Executive"],
            ["joining_date", "Date of joining", "e.g. 15 October 2026"],
            ["ctc", "Annual CTC (Rs.)", "e.g. 6,00,000"],
            ["location", "Work location", "e.g. Bangalore"],
            ["hr_name", "HR signatory name", "e.g. Rahul Verma, HR Manager"],
        ],
        "render": _render_offer,
    },
    "appointment-letter": {
        "title": "Appointment Letter",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["role", "Job title", ""],
            ["department", "Department", "e.g. Sales"],
            ["joining_date", "Date of joining", ""],
            ["ctc", "Annual CTC (Rs.)", ""],
            ["probation", "Probation period", "e.g. 3 months"],
            ["location", "Work location", ""],
            ["hr_name", "HR signatory name", ""],
        ],
        "render": _render_appointment,
    },
    "increment-letter": {
        "title": "Salary Increment Letter",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["role", "Current job title", ""],
            ["new_ctc", "Revised annual CTC (Rs.)", ""],
            ["hike", "Increase", "e.g. 12% or Rs. 72,000"],
            ["effective_date", "Effective date", ""],
            ["hr_name", "HR signatory name", ""],
        ],
        "render": _render_increment,
    },
    "promotion-letter": {
        "title": "Promotion Letter",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["old_role", "Current job title", ""],
            ["new_role", "New job title", ""],
            ["effective_date", "Effective date", ""],
            ["location", "Location", ""],
            ["hr_name", "HR signatory name", ""],
        ],
        "render": _render_promotion,
    },
    "experience-certificate": {
        "title": "Experience Certificate",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["role", "Job title", ""],
            ["start_date", "Employment start date", ""],
            ["end_date", "Employment end date", ""],
            ["hr_name", "HR signatory name", ""],
        ],
        "render": _render_experience,
    },
    "relieving-letter": {
        "title": "Relieving Letter",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["role", "Job title", ""],
            ["last_day", "Last working day", ""],
            ["hr_name", "HR signatory name", ""],
        ],
        "render": _render_relieving,
    },
    "warning-letter": {
        "title": "Warning Letter",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["role", "Job title", ""],
            ["incident_date", "Date of the incident", ""],
            ["issue", "Describe the issue", "e.g. Repeated unapproved absence on..."],
            ["hr_name", "HR signatory name", ""],
        ],
        "render": _render_warning,
    },
    "exit-interview": {
        "title": "Exit Interview Form",
        "fields": [
            ["company", "Company name", ""],
            ["employee", "Employee name", ""],
            ["role", "Job title", ""],
            ["last_day", "Last working day", ""],
            ["reason", "Stated reason for leaving", ""],
            ["manager", "Reporting manager", ""],
            ["hr_name", "HR interviewer name", ""],
        ],
        "render": _render_exit,
    },
}

HRDOC_BODY = """
<section class="page-hero"><div class="container">
  <span class="tag live">Live</span>
  <h1 style="margin-top:12px">HR Document Generator</h1>
  <p>Fill a short form, download a ready-to-edit Word document. Free, no
  sign-up, nothing stored.</p>
</div></section>
<section class="section"><div class="container" style="max-width:780px">
  <div class="pill-tabs" id="tabs"></div>
  <div class="card">
    <div id="docForm"></div>
    <div class="toolbar"><button class="btn" onclick="genDoc()">Generate Word document</button></div>
    <div class="err" id="err"></div>
    <div class="hint">The document downloads as a .docx file you can edit in
    Word or Google Docs. It is a template - have HR/legal review before use.</div>
  </div>
</div></section>
<script>
var DOCS = __DOCS_JSON__;
var cur = Object.keys(DOCS)[0];
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function buildTabs() {
  var h = "";
  Object.keys(DOCS).forEach(function (id) {
    h += '<button' + (id === cur ? ' class="active"' : '')
      + ' onclick="pick(\\'' + id + '\\')">' + esc(DOCS[id].title) + '</button>';
  });
  document.getElementById("tabs").innerHTML = h;
}
function pick(id) { cur = id; buildTabs(); buildForm(); }
function buildForm() {
  var d = DOCS[cur], h = "";
  d.fields.forEach(function (f) {
    h += '<div class="field"><label>' + esc(f[1]) + '</label>'
      + '<input id="d_' + f[0] + '" type="text" placeholder="' + esc(f[2]) + '"></div>';
  });
  document.getElementById("docForm").innerHTML = h;
  document.getElementById("err").textContent = "";
}
function genDoc() {
  var d = DOCS[cur], fields = {}, missing = false;
  d.fields.forEach(function (f) {
    var v = document.getElementById("d_" + f[0]).value.trim();
    fields[f[0]] = v;
    if (!v) missing = true;
  });
  var err = document.getElementById("err");
  if (missing) { err.textContent = "Please fill every field so the document is complete."; return; }
  err.textContent = "";
  fetch("/api/hr/document/" + cur, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({fields: fields})
  }).then(function (r) {
    if (!r.ok) {
      return r.json().then(function (j) { throw new Error(j.error || "Could not generate the document."); });
    }
    return r.blob();
  }).then(function (blob) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = cur + ".docx";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 800);
  }).catch(function (e) { err.textContent = e.message || "Something went wrong."; });
}
buildTabs();
buildForm();
</script>
"""


def hr_documents_page() -> str:
    cfg = {
        slug: {"title": spec["title"], "fields": spec["fields"]}
        for slug, spec in HR_DOCS.items()
    }
    body = HRDOC_BODY.replace("__DOCS_JSON__", json.dumps(cfg))
    return page("HR Document Generator",
                "Generate HR documents as Word files: offer letter, appointment letter, increment letter, promotion letter, experience certificate, relieving letter, warning letter and exit interview form.",
                "/hr-career", body)



# ----------------------------------------------------------------------
# Document parsing
# ----------------------------------------------------------------------

IMAGE_MIMES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _ext(filename: str) -> str:
    return os.path.splitext(filename.lower())[1]


def parse_document(filename: str, data: bytes) -> dict:
    """Return {'text': str|None, 'raw': bytes|None, 'raw_mime': str|None,
    'kind': str, 'detail': str}. Text docs give text; images and scanned
    PDFs are passed to the AI as raw bytes."""
    ext = _ext(filename)

    if ext in IMAGE_MIMES:
        return {"text": None, "raw": data, "raw_mime": IMAGE_MIMES[ext],
                "kind": "image", "detail": "Image"}

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            parts = []
            for p in reader.pages:
                parts.append(p.extract_text() or "")
            text = "\n\n".join(parts).strip()
            pages = len(reader.pages)
        except Exception:
            text, pages = "", 0
        if len(text.strip()) < 30:
            # Scanned / image-only PDF: let the AI read the file itself.
            return {"text": None, "raw": data, "raw_mime": "application/pdf",
                    "kind": "pdf", "detail": f"PDF, {pages} page(s) - read visually"}
        return {"text": text, "raw": None, "raw_mime": None,
                "kind": "pdf", "detail": f"PDF, {pages} page(s)"}

    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(data))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for tbl in doc.tables:
            for row in tbl.rows:
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    parts.append(" | ".join(cells))
        text = "\n".join(parts).strip()
        if not text:
            raise ValueError("Could not read any text from this Word file.")
        return {"text": text, "raw": None, "raw_mime": None,
                "kind": "docx", "detail": "Word document"}

    if ext in (".xlsx", ".xls"):
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        parts = []
        for ws in wb.worksheets:
            parts.append(f"Sheet: {ws.title}")
            for row in ws.iter_rows(values_only=True):
                vals = ["" if v is None else str(v) for v in row]
                if any(v.strip() for v in vals):
                    parts.append("\t".join(vals))
        text = "\n".join(parts).strip()
        if not text:
            raise ValueError("This spreadsheet appears to be empty.")
        return {"text": text, "raw": None, "raw_mime": None,
                "kind": "excel", "detail": f"Excel, {len(wb.worksheets)} sheet(s)"}

    if ext in (".txt", ".csv"):
        for enc in ("utf-8", "utf-16", "latin-1"):
            try:
                text = data.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode this text file.")
        text = text.strip()
        if not text:
            raise ValueError("This file appears to be empty.")
        label = "CSV" if ext == ".csv" else "Text file"
        return {"text": text, "raw": None, "raw_mime": None,
                "kind": ext[1:], "detail": label}

    raise ValueError(
        "That file type is not supported yet. Please use PDF, Word, TXT, "
        "CSV, Excel, or an image (PNG / JPG / WEBP)."
    )


# ----------------------------------------------------------------------
# In-memory document store (per session; Supabase arrives in Phase 4)
# ----------------------------------------------------------------------

DOCS: dict = {}
DOCS_LOCK = threading.Lock()


def store_doc(parsed: dict, filename: str, size: int) -> str:
    doc_id = uuid.uuid4().hex[:16]
    text = parsed.get("text")
    if text and len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]
    with DOCS_LOCK:
        # expire old docs first, then evict oldest above the cap
        now = time.time()
        for k in [k for k, v in DOCS.items() if now - v["created"] > DOC_TTL_SECONDS]:
            DOCS.pop(k, None)
        while len(DOCS) >= MAX_DOCS_IN_MEMORY:
            oldest = min(DOCS, key=lambda k: DOCS[k]["created"])
            DOCS.pop(oldest, None)
        DOCS[doc_id] = {
            "created": time.time(),
            "name": filename,
            "size": size,
            "kind": parsed["kind"],
            "detail": parsed["detail"],
            "text": text,
            "raw": parsed.get("raw"),
            "raw_mime": parsed.get("raw_mime"),
            "chars": len(text) if text else 0,
            "extraction": None,
        }
    return doc_id


def get_doc(doc_id: str):
    with DOCS_LOCK:
        return DOCS.get(doc_id)


# ----------------------------------------------------------------------
# Simple per-IP rate limiting for AI endpoints
# ----------------------------------------------------------------------

AI_CALLS: dict = defaultdict(deque)
RATE_LOCK = threading.Lock()


def rate_ok(ip: str) -> bool:
    now = time.time()
    with RATE_LOCK:
        q = AI_CALLS[ip]
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= RATE_LIMIT_AI_PER_HOUR:
            return False
        q.append(now)
        if len(AI_CALLS) > 5000:
            AI_CALLS.clear()
        return True


# ----------------------------------------------------------------------
# Gemini
# ----------------------------------------------------------------------

_gemini_client = None
_gemini_model = None


def gemini_ready() -> bool:
    return bool(GEMINI_API_KEY)


def _client():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


def gemini_generate(doc: dict, instruction: str, json_mode: bool = False) -> str:
    """Call Gemini with the document + instruction, with model fallback."""
    from google.genai import types

    global _gemini_model
    parts = []
    if doc.get("raw"):
        parts.append(types.Part.from_bytes(data=doc["raw"], mime_type=doc["raw_mime"]))
        parts.append(types.Part.from_text(
            text="The file above is the user's document, named "
                 f"'{doc['name']}'.\n\n{instruction}"))
    else:
        parts.append(types.Part.from_text(
            text=f"The user uploaded a document named '{doc['name']}'. "
                 "Here is its extracted text:\n\n---\n"
                 f"{doc['text']}\n---\n\n{instruction}"))

    config = None
    if json_mode:
        config = types.GenerateContentConfig(response_mime_type="application/json")

    def _call(model):
        resp = _client().models.generate_content(
            model=model, contents=[types.Content(role="user", parts=parts)],
            config=config)
        return (resp.text or "").strip()

    models = [_gemini_model] if _gemini_model else list(GEMINI_MODELS)
    last_err = None
    for model in models:
        try:
            out = _call(model)
            _gemini_model = model
            return out
        except Exception as e:  # try next model on model-not-found style errors
            last_err = e
            msg = str(e).lower()
            # Move to the next candidate model on renames (404) and on
            # transient capacity/quota errors (503/429) - a single congested
            # model must not take the whole feature down.
            if ("not found" in msg or "no longer available" in msg
                    or "not supported" in msg or "503" in msg
                    or "unavailable" in msg or "high demand" in msg
                    or "429" in msg or "resource_exhausted" in msg
                    or "quota" in msg):
                continue
            raise

    # Dynamic fallback: ask the API which flash models this key can use.
    try:
        for m in _client().models.list():
            short = (getattr(m, "name", "") or "").split("/")[-1]
            if "flash" not in short or short in models:
                continue
            try:
                out = _call(short)
                _gemini_model = short
                return out
            except Exception as e:
                last_err = e
                continue
    except Exception as e:
        last_err = e
    raise RuntimeError(f"AI model error: {last_err}")


SUMMARY_PROMPT = (
    "Write a clear, well-structured summary of this document for a busy "
    "professional. Use short headings (## style) and bullet points. Cover: "
    "what the document is, the key points, important figures/dates/amounts, "
    "and the main takeaways. Keep it under 400 words. Base everything only "
    "on the document - do not invent facts."
)

ANALYZE_PROMPT = (
    "Do a deep, practical analysis of this document. Use short headings "
    "(## style) and bullets. Cover: 1) what kind of document this is and "
    "its purpose, 2) strengths, 3) weaknesses, gaps or unclear parts, "
    "4) risks, red flags or anything the reader should double-check, "
    "5) important missing information, 6) concrete suggestions. Be honest "
    "and specific. Base everything only on the document."
)

EXTRACT_PROMPT = (
    "Extract the key structured information from this document. "
    "Respond with JSON only, in exactly this shape:\n"
    '{"fields": {"Field name": "value", ...}, '
    '"tables": [{"name": "table name", "rows": [["col1","col2"],["v1","v2"]]}]}\n'
    "Rules: choose field names that fit the document type (for an invoice: "
    "invoice number, date, vendor, amounts, tax; for a resume: name, "
    "skills, experience, education; etc.). Keep values short. Include at "
    "most 25 fields. Include tables only if the document clearly contains "
    "tabular data; rows must all be arrays of strings. If nothing "
    "structured exists, return empty fields and no tables."
)

CHAT_PROMPT = (
    "You are Nexora's document assistant. Answer the user's question using "
    "ONLY the document provided. If the answer is not in the document, say "
    "so plainly. Be concise and specific; quote figures exactly.\n\n"
    "Question: {question}"
)


def err_response(status: int, message: str) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status)


def doc_or_404(doc_id: str):
    doc = get_doc(doc_id)
    if not doc:
        return None, err_response(
            404, "That document is no longer available. Please upload it again.")
    return doc, None


# ----------------------------------------------------------------------
# Page routes
# ----------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    return home_page()


@app.get("/document-ai", response_class=HTMLResponse)
async def document_ai() -> str:
    return document_ai_page()


@app.get("/hr-career", response_class=HTMLResponse)
async def hr_career() -> str:
    return hr_career_page()


@app.get("/resume-builder", response_class=HTMLResponse)
async def resume_builder() -> str:
    return career_tool_page("resume-builder")


@app.get("/jd-builder", response_class=HTMLResponse)
async def jd_builder() -> str:
    return career_tool_page("jd-builder")


@app.get("/career/{slug}", response_class=HTMLResponse)
async def career_tool(slug: str) -> str:
    if slug not in CAREER_TOOLS:
        return not_found_page()
    return career_tool_page(slug)


@app.get("/hr/calculators", response_class=HTMLResponse)
async def hr_calculators() -> str:
    return calculators_page()


@app.get("/hr/documents", response_class=HTMLResponse)
async def hr_documents() -> str:
    return hr_documents_page()


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "nexora"})


# ----------------------------------------------------------------------
# Document AI API
# ----------------------------------------------------------------------


@app.get("/api/config")
async def api_config() -> JSONResponse:
    return JSONResponse({"ai_ready": gemini_ready()})


@app.post("/api/documents")
async def api_upload(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    if not gemini_ready():
        return err_response(503, "The AI engine is being configured. Please try again shortly.")
    ip = request.client.host if request.client else "unknown"
    if not rate_ok(ip):
        return err_response(429, "Too many requests. Please wait a while and try again.")
    data = await file.read()
    if not data:
        return err_response(400, "That file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        return err_response(400, "That file is larger than 12 MB. Please use a smaller file.")
    name = os.path.basename(file.filename or "document")[:120]
    try:
        parsed = parse_document(name, data)
    except ValueError as e:
        return err_response(400, str(e))
    except Exception:
        return err_response(400, "Could not read that file. Please try another one.")
    doc_id = store_doc(parsed, name, len(data))
    chars = parsed.get("text")
    meta = parsed["detail"]
    if chars:
        words = len(chars.split())
        meta += f" - about {words:,} words read"
    return JSONResponse({"doc_id": doc_id, "name": name, "meta": meta})


@app.get("/api/documents/{doc_id}")
async def api_doc_info(doc_id: str) -> JSONResponse:
    doc, err = doc_or_404(doc_id)
    if err:
        return err
    preview = (doc["text"][:2000] if doc.get("text") else "")
    return JSONResponse({
        "name": doc["name"], "detail": doc["detail"],
        "chars": doc["chars"], "preview": preview,
    })


def _ai_guard(request: Request, doc_id: str):
    if not gemini_ready():
        return None, err_response(503, "The AI engine is being configured. Please try again shortly.")
    doc, err = doc_or_404(doc_id)
    if err:
        return None, err
    ip = request.client.host if request.client else "unknown"
    if not rate_ok(ip):
        return None, err_response(429, "You have reached the free usage limit for now. Please try again later.")
    return doc, None


@app.post("/api/documents/{doc_id}/summary")
async def api_summary(request: Request, doc_id: str) -> JSONResponse:
    doc, err = _ai_guard(request, doc_id)
    if err:
        return err
    try:
        out = gemini_generate(doc, SUMMARY_PROMPT)
    except Exception:
        traceback.print_exc()
        return err_response(502, "The AI could not process this right now. Please try again.")
    return JSONResponse({"summary": out})


@app.post("/api/documents/{doc_id}/analyze")
async def api_analyze(request: Request, doc_id: str) -> JSONResponse:
    doc, err = _ai_guard(request, doc_id)
    if err:
        return err
    try:
        out = gemini_generate(doc, ANALYZE_PROMPT)
    except Exception:
        traceback.print_exc()
        return err_response(502, "The AI could not process this right now. Please try again.")
    return JSONResponse({"analysis": out})


@app.post("/api/documents/{doc_id}/extract")
async def api_extract(request: Request, doc_id: str) -> JSONResponse:
    doc, err = _ai_guard(request, doc_id)
    if err:
        return err
    try:
        raw = gemini_generate(doc, EXTRACT_PROMPT, json_mode=True)
        data = json.loads(raw)
    except Exception:
        traceback.print_exc()
        return err_response(502, "Could not extract data from this document. Please try again.")
    fields = data.get("fields") if isinstance(data, dict) else {}
    tables = data.get("tables") if isinstance(data, dict) else []
    if not isinstance(fields, dict):
        fields = {}
    fields = {str(k)[:80]: ("" if v is None else str(v)[:500])
              for k, v in list(fields.items())[:25]}
    clean_tables = []
    if isinstance(tables, list):
        for t in tables[:5]:
            if not isinstance(t, dict):
                continue
            rows = t.get("rows")
            if not isinstance(rows, list):
                continue
            rows = [[str(c)[:200] for c in r] if isinstance(r, list) else [str(r)[:200]]
                    for r in rows[:200]]
            if rows:
                clean_tables.append({"name": str(t.get("name") or "Table")[:80], "rows": rows})
    with DOCS_LOCK:
        if doc_id in DOCS:
            DOCS[doc_id]["extraction"] = {"fields": fields, "tables": clean_tables,
                                          "name": doc["name"]}
    return JSONResponse({"fields": fields, "tables": clean_tables})


@app.post("/api/documents/{doc_id}/chat")
async def api_chat(request: Request, doc_id: str) -> JSONResponse:
    doc, err = _ai_guard(request, doc_id)
    if err:
        return err
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    question = str(payload.get("message") or "").strip()[:2000]
    if not question:
        return err_response(400, "Please type a question.")
    history = payload.get("history")
    ctx = ""
    if isinstance(history, list):
        turns = []
        for h in history[-10:]:
            if not isinstance(h, dict):
                continue
            role = "User" if h.get("role") == "user" else "Assistant"
            turns.append(f"{role}: {str(h.get('text', ''))[:1000]}")
        if turns:
            ctx = "\n\nConversation so far:\n" + "\n".join(turns)
    prompt = CHAT_PROMPT.replace("{question}", question) + ctx
    try:
        out = gemini_generate(doc, prompt)
    except Exception:
        traceback.print_exc()
        return err_response(502, "The AI could not process this right now. Please try again.")
    return JSONResponse({"answer": out})


@app.get("/api/documents/{doc_id}/export.xlsx")
async def api_export(doc_id: str) -> StreamingResponse:
    doc, err = doc_or_404(doc_id)
    if err:
        return err
    extraction = doc.get("extraction")
    if not extraction:
        return err_response(400, "Run Extract data first, then download the Excel file.")
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Extracted data"
    ws.append(["Field", "Value"])
    for k, v in extraction["fields"].items():
        ws.append([k, v])
    for t in extraction["tables"]:
        sheet = wb.create_sheet(title=re.sub(r"[\\/*?\[\]:]", " ", t["name"])[:28] or "Table")
        for row in t["rows"]:
            sheet.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.splitext(doc["name"])[0])[:40] or "nexora"
    headers = {"Content-Disposition": f'attachment; filename="{base}-extracted.xlsx"'}
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


def not_found_page() -> str:
    body = """
<section class="hero"><div class="container">
  <p class="kicker">Page not found</p>
  <h1>That page does not exist yet</h1>
  <p class="lede">The link may be old, or this part of Nexora is still being built.</p>
  <p style="margin-top:22px"><a class="btn" href="/">Back to home</a></p>
</div></section>
"""
    return page("Page not found", "This page does not exist.", "", body)


# ----------------------------------------------------------------------
# Phase 3 API: career tools, HR documents, DOCX download
# ----------------------------------------------------------------------


def _clean_md(s: str) -> str:
    return str(s).replace("**", "").replace("__", "").replace("`", "")


def md_to_docx_bytes(title: str, text: str) -> bytes:
    from docx import Document
    doc = Document()
    if title:
        doc.add_heading(_clean_md(title), level=1)
    for line in str(text).splitlines():
        t = line.strip()
        if not t:
            continue
        if t == "---":
            continue
        if t.startswith("## "):
            doc.add_heading(_clean_md(t[3:]), level=2)
        elif t.startswith("# "):
            doc.add_heading(_clean_md(t[2:]), level=2)
        elif t.startswith("- ") or t.startswith("* "):
            doc.add_paragraph(_clean_md(t[2:]), style="List Bullet")
        elif re.match(r"^\d+[.)]\s", t):
            doc.add_paragraph(_clean_md(re.sub(r"^\d+[.)]\s", "", t)),
                              style="List Number")
        else:
            doc.add_paragraph(_clean_md(t))
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _docx_response(data: bytes, filename: str) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(data), media_type=DOCX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.post("/api/career/{slug}")
async def api_career(slug: str, request: Request) -> JSONResponse:
    spec = CAREER_TOOLS.get(slug)
    if not spec:
        return err_response(404, "Unknown tool.")
    if not gemini_ready():
        return err_response(503, "The AI engine is being configured. Please try again shortly.")
    ip = request.client.host if request.client else "unknown"
    if not rate_ok(ip):
        return err_response(429, "You have reached the free usage limit for now. Please try again later.")
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    raw_fields = payload.get("fields")
    fields = {}
    if isinstance(raw_fields, dict):
        fields = {str(k)[:40]: str(v)[:4000] for k, v in raw_fields.items()}
    for req in spec.get("required", []):
        if not fields.get(req, "").strip():
            label = next((f[1] for f in spec["fields"] if f[0] == req), req)
            return err_response(400, f"Please fill in: {label}.")
    doc = None
    doc_id = str(payload.get("doc_id") or "").strip()
    if doc_id:
        doc, err = doc_or_404(doc_id)
        if err:
            return err
    source_text = str(payload.get("source_text") or "")[:30000].strip()
    if doc is None and source_text:
        doc = {"name": spec["source"]["label"] if spec.get("source") else "your input",
               "text": source_text, "raw": None}
    if doc is None:
        if spec.get("source") and slug not in ("recruitment-optimizer",):
            return err_response(400, "Please paste or upload "
                                + spec["source"]["label"].lower() + ".")
        text = "\n".join(f"{k}: {v}" for k, v in fields.items() if v.strip())
        if not text.strip():
            return err_response(400, "Please fill in the form first.")
        doc = {"name": "your request", "text": text, "raw": None}
    prompt = spec["prompt"].format_map(_F(fields))
    try:
        out = gemini_generate(doc, prompt)
    except Exception:
        traceback.print_exc()
        return err_response(502, "The AI could not process this right now. Please try again.")
    return JSONResponse({"result": out})


@app.post("/api/hr/document/{slug}")
async def api_hr_document(slug: str, request: Request):
    spec = HR_DOCS.get(slug)
    if not spec:
        return err_response(404, "Unknown document.")
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    raw_fields = payload.get("fields") if isinstance(payload, dict) else {}
    fields = {}
    if isinstance(raw_fields, dict):
        fields = {str(k)[:40]: str(v)[:300] for k, v in raw_fields.items()}
    text = spec["render"](fields).replace("__DATE__", _today())
    data = md_to_docx_bytes("", text)
    return _docx_response(data, f"{slug}.docx")


@app.post("/api/download-docx")
async def api_download_docx(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    title = str(payload.get("title") or "Nexora document")[:80]
    content = str(payload.get("content") or "")[:60000]
    if not content.strip():
        return err_response(400, "Nothing to download yet.")
    data = md_to_docx_bytes(title, content)
    fname = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "nexora"
    return _docx_response(data, f"{fname}.docx")



@app.exception_handler(404)
async def not_found(request: Request, exc: Exception) -> HTMLResponse:
    body = """
<section class="hero"><div class="container">
  <p class="kicker">Page not found</p>
  <h1>That page does not exist yet</h1>
  <p class="lede">The link may be old, or this part of Nexora is still being built.</p>
  <p style="margin-top:22px"><a class="btn" href="/">Back to home</a></p>
</div></section>
"""
    return HTMLResponse(page("Page not found", "This page does not exist.", "", body), status_code=404)
