"""
Nexora - production application (Phase 1 shell + Phase 2 Document AI).

FastAPI website serving the Nexora landing pages plus the working
Document AI workspace: upload a document, summarize it, chat with it,
extract structured data (Excel export) and run a deep analysis.

Routes:
  /                Home
  /document-ai     Document AI workspace (live)
  /hr-career       HR & Career section (placeholder)
  /resume-builder  Resume Builder + ATS Optimizer (featured placeholder)
  /jd-builder      JD Builder + Recruitment Optimizer (featured placeholder)
  /health          JSON health check for Render

API routes (Document AI):
  POST /api/documents                     upload a document
  GET  /api/documents/{doc_id}            document info + text preview
  POST /api/documents/{doc_id}/summary    AI summary
  POST /api/documents/{doc_id}/chat       AI Q&A on the document
  POST /api/documents/{doc_id}/extract    AI structured data extraction (JSON)
  POST /api/documents/{doc_id}/analyze    AI deep analysis
  GET  /api/documents/{doc_id}/export.xlsx  Excel export of last extraction

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
GEMINI_MODELS = ["gemini-3.8-flash"]

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


def hr_career_page() -> str:
    body = f"""
<section class="page-hero"><div class="container">
  <h1>HR &amp; Career Intelligence</h1>
  <p>Practical AI tools for job seekers and HR teams - resumes, job
  descriptions, letters and calculators.</p>
</div></section>
<section class="section"><div class="container">
  <div class="grid three">
    {linked_card("/resume-builder", "resume", "Resume Builder",
                 "Professional resumes with free analysis and paid expert improvements.",
                 "Explore", badge="Featured")}
    {card("target", "ATS Optimizer", "Beat the software that screens resumes before humans see them.", badge="Soon")}
    {card("search", "Resume Analyzer", "Find weaknesses, missing keywords and formatting issues.", badge="Soon")}
    {linked_card("/jd-builder", "pen", "JD Builder",
                 "Clear, complete job descriptions written in minutes.",
                 "Explore", badge="Featured")}
    {card("search", "JD Analyzer", "Check a job description for gaps, bias and clarity.", badge="Soon")}
    {card("check", "Recruitment Optimizer", "Improve job ads and screening for better hiring.", badge="Soon")}
    {card("letter", "Cover Letter Builder", "Tailored cover letters matched to each job.", badge="Soon")}
    {card("doc", "Offer Letter Analyzer", "Understand every clause of an offer before you sign.", badge="Soon")}
    {card("calc", "HR Calculators", "CTC, take-home, increment, gratuity, notice period and more.", badge="Soon")}
  </div>
  <div class="note">HR &amp; Career tools move here after Document AI.
  Resume Builder and JD Builder arrive first, with free analysis and
  optional paid improvements.</div>
</div></section>
"""
    return page("HR &amp; Career", "HR and career AI tools: resume builder, ATS optimizer, JD builder, letters and calculators.", "/hr-career", body)


def resume_builder_page() -> str:
    body = f"""
<section class="page-hero"><div class="container">
  <span class="tag featured">Featured</span>
  <h1 style="margin-top:12px">Resume Builder + ATS Optimizer</h1>
  <p>Build a professional resume, see exactly where it is weak, and get it
  fixed so it passes both recruiters and applicant tracking systems.</p>
</div></section>
<section class="section"><div class="container">
  <div class="split">
    <div class="card">
      <h3>Free</h3>
      <ul class="checklist">
        <li>Resume analysis</li>
        <li>ATS assessment</li>
        <li>Weakness identification</li>
        <li>Missing keywords</li>
        <li>Formatting issue report</li>
        <li>Clear suggestions</li>
      </ul>
    </div>
    <div class="card">
      <h3>Paid improvements</h3>
      <ul class="checklist">
        <li>Fix every weakness found</li>
        <li>Full professional rewrite</li>
        <li>ATS optimization</li>
        <li>Job-specific optimization</li>
        <li>Professional wording</li>
        <li>Download as DOCX / PDF</li>
      </ul>
    </div>
  </div>
  <p style="margin-top:22px"><span class="btn disabled">Coming soon on Nexora web</span></p>
  <div class="note">The Resume Builder is the first paid product being moved
  to this platform. Free analysis first - pay only if you want the
  improvements done for you.</div>
</div></section>
"""
    return page("Resume Builder", "Resume Builder and ATS Optimizer: free resume analysis with optional paid professional improvements.", "/resume-builder", body)


def jd_builder_page() -> str:
    body = f"""
<section class="page-hero"><div class="container">
  <span class="tag featured">Featured</span>
  <h1 style="margin-top:12px">JD Builder + Recruitment Optimizer</h1>
  <p>Write complete, clear job descriptions in minutes - and improve them so
  they attract the right candidates.</p>
</div></section>
<section class="section"><div class="container">
  <div class="split">
    <div class="card">
      <h3>Free</h3>
      <ul class="checklist">
        <li>Job description analysis</li>
        <li>Clarity and completeness check</li>
        <li>Missing sections identified</li>
        <li>Vague wording flagged</li>
        <li>Candidate-fit suggestions</li>
      </ul>
    </div>
    <div class="card">
      <h3>Paid improvements</h3>
      <ul class="checklist">
        <li>Full JD rewrite</li>
        <li>Role-specific optimization</li>
        <li>Professional structure and wording</li>
        <li>Screening question suggestions</li>
        <li>Download as DOCX / PDF</li>
      </ul>
    </div>
  </div>
  <p style="margin-top:22px"><span class="btn disabled">Coming soon on Nexora web</span></p>
  <div class="note">The JD Builder is the second paid product on the
  roadmap. Analyze a job description free - pay only for the improved,
  ready-to-post version.</div>
</div></section>
"""
    return page("JD Builder", "JD Builder and Recruitment Optimizer: write and improve job descriptions that attract the right candidates.", "/jd-builder", body)

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
            if "not found" in msg or "no longer available" in msg or "not supported" in msg:
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
    return resume_builder_page()


@app.get("/jd-builder", response_class=HTMLResponse)
async def jd_builder() -> str:
    return jd_builder_page()


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
