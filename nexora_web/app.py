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

from fastapi import FastAPI, Request, UploadFile, File, HTTPException

from web_content import *  # noqa: F401,F403 - HTML/CSS/content constants
from pdf_tools import TOOLS as PDF_TOOL_SPECS, ORDER as PDF_TOOL_ORDER, ToolError, run_tool
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse, Response

app = FastAPI(title="Nexora", docs_url=None, redoc_url=None, openapi_url=None)

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Fast, cost-efficient model first; fallbacks protect against renames.
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-flash-lite-latest", "gemini-3.1-flash-lite"]

# Phase 4: Supabase (server-side only; never expose these to the browser).
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()

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
    ("/pro", "Pro"),
]

# ----------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Small inline SVG icons (24x24, currentColor)
# ----------------------------------------------------------------------


# Emoji shown on each option card (conveys the tool's meaning at a glance).


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
        f'<div class="navlinks">{"".join(links)}'
        '<a href="/login" id="authLink" class="auth-link">Sign in</a>'
        '<a href="/auth/logout" id="signOutLink" class="auth-link" style="display:none">Sign out</a></div>'
        "</div></nav>"
        "<script>fetch(\"/api/me\",{credentials:\"same-origin\",cache:\"no-store\"}).then(function(r){return r.json()}).then(function(d){"
        "var a=document.getElementById(\"authLink\");if(!a)return;"
        "if(d.authenticated){var n=(d.name||d.email||\"Account\").split(\" \")[0];"
        "a.textContent=n;a.removeAttribute(\"href\");a.title=\"Signed in as \"+(d.email||n);"
        "document.getElementById(\"signOutLink\").style.display=\"\";}"
        "}).catch(function(){});</script>"
    )


def footer_html() -> str:
    return (
        '<footer class="footer"><div class="container row">'
        '<a class="brand" href="/">Nexo<span>ra</span></a>'
        "<span>AI-powered productivity tools for documents, HR &amp; careers.</span>"
        '<span style="margin-left:auto;opacity:.55;font-size:13px">Built with Instinct</span>'
        '<a href="/resume-service">Online document help</a><a href="/privacy">Privacy</a><a href="/terms">Terms</a><span>&copy; 2026 Nexora</span>'
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
        f'<div class="card-icon">{EMOJI.get(icon, EMOJI["doc"])}</div>'
        f"<h3>{title}</h3><p>{text}</p>{badge_html}{extra}</div>"
    )


def linked_card(href: str, icon: str, title: str, text: str, cta: str, badge: str = "") -> str:
    badge_html = f'<span class="tag {badge.lower()}">{badge}</span>' if badge else ""
    return (
        f'<a class="card card-link" href="{href}">'
        f'<div class="card-icon">{EMOJI.get(icon, EMOJI["doc"])}</div>'
        f"<h3>{title}</h3><p>{text}</p>"
        f'{badge_html}<p style="margin-top:12px"><strong style="color:var(--accent)">{cta} &rarr;</strong></p>'
        "</a>"
    )

# ----------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Phase 5: Authentication (Supabase Auth, Google OAuth via PKCE)
# ----------------------------------------------------------------------

SESSION_COOKIE = "nx_session"
PKCE_COOKIE = "nx_pkce"
SITE_URL = os.environ.get("SITE_URL", "https://nexora-web-q7rn.onrender.com").rstrip("/")


def auth_ready() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)


def _session_key() -> bytes:
    import hashlib
    secret = (os.environ.get("SESSION_SECRET", "").strip()
              or SUPABASE_SERVICE_KEY or "nexora-dev-secret")
    return hashlib.sha256(secret.encode()).digest()


def _sign(data: str) -> str:
    import hmac, hashlib
    sig = hmac.new(_session_key(), data.encode(), hashlib.sha256).hexdigest()[:32]
    return data + "." + sig


def _unsign(signed: str):
    import hmac, hashlib
    if not signed or "." not in signed:
        return None
    data, sig = signed.rsplit(".", 1)
    expect = hmac.new(_session_key(), data.encode(), hashlib.sha256).hexdigest()[:32]
    return data if hmac.compare_digest(sig, expect) else None


def _b64url(raw: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64url_decode(s: str) -> bytes:
    import base64
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _auth_call(path: str, form: dict = None, token: str = None):
    """Call Supabase Auth REST. Returns (status, parsed-json)."""
    import urllib.request
    import urllib.parse
    import urllib.error
    url = SUPABASE_URL + "/auth/v1/" + path
    data = json.dumps(form).encode() if form is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("apikey", SUPABASE_ANON_KEY)
    if form is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception:
        traceback.print_exc()
        return 0, {}


def _load_session(request: Request):
    """Return (payload_dict, expired) or (None, False)."""
    data = _unsign(request.cookies.get(SESSION_COOKIE, ""))
    if not data:
        return None, False
    try:
        payload = json.loads(_b64url_decode(data).decode())
    except Exception:
        return None, False
    return payload, payload.get("exp", 0) < time.time()


def _session_value(tokens: dict) -> str:
    payload = {
        "at": tokens["access_token"],
        "rt": tokens.get("refresh_token", ""),
        "exp": int(time.time()) + int(tokens.get("expires_in", 3600)) - 120,
    }
    return _sign(_b64url(json.dumps(payload).encode()))


# ----------------------------------------------------------------------
# ilovepdf-style tools grid (home + hub)
# ----------------------------------------------------------------------

HOME_TOOLS = [
    *[(f"/pdf/{slug}", PDF_TOOL_SPECS[slug]["icon"], PDF_TOOL_SPECS[slug]["title"],
       PDF_TOOL_SPECS[slug]["desc"], "pdf") for slug in PDF_TOOL_ORDER],
    ("/document-ai", "doc", "Document AI",
     "Summaries, answers and data extraction from any document.", "document"),
    ("/resume-builder", "resume", "Resume Builder",
     "A complete, ATS-friendly resume written from your details.", "career"),
    ("/career/resume-analyzer", "search", "Resume Analyzer",
     "Score, weaknesses, missing keywords and concrete fixes.", "career"),
    ("/resume-ats-checker", "target", "Resume ATS Checker",
     "Match score, missing keywords and tailoring advice for a specific job.", "career"),
    ("/jd-builder", "pen", "JD Builder",
     "Complete job descriptions with the right structure and tone.", "career"),
    ("/jd-quality-checker", "mag", "JD Quality Checker",
     "Find gaps, bias and clarity issues before you post a JD.", "career"),
    ("/career/recruitment-optimizer", "megaphone", "Recruitment Optimizer",
     "Sourcing channels, screening questions and a faster hiring process.", "career"),
    ("/cover-letter-generator", "letter", "Cover Letter Generator",
     "Tailored cover letters that match your resume to the job.", "career"),
    ("/offer-letter-analyzer", "page", "Offer Letter Analyzer",
     "Clause-by-clause explanation, red flags and negotiation points.", "career"),
    ("/ctc-calculator", "calc", "CTC Breakdown Calculator",
     "See how any CTC splits into Basic, HRA, PF, gratuity and allowances.", "calc"),
    ("/salary-calculator", "money", "Take-home Salary Calculator",
     "Estimate your monthly in-hand salary from any CTC.", "calc"),
    ("/increment-calculator", "chart", "Increment Calculator",
     "Your new salary after a hike - per year and per month.", "calc"),
    ("/gratuity-calculator", "gift", "Gratuity Calculator",
     "Gratuity payable under the Payment of Gratuity Act.", "calc"),
    ("/notice-period-calculator", "calendar", "Notice Period Calculator",
     "Find your exact last working day from your resignation date.", "calc"),
    ("/hr/documents", "folder", "HR Document Generator",
     "Offer, appointment, increment, promotion, experience, relieving letters and more - as Word files.", "docs"),
]

FILTER_JS = """<script>
function filterTools(cat, btn) {
  document.querySelectorAll(".cat-pills button").forEach(function (b) { b.classList.remove("active"); });
  btn.classList.add("active");
  document.querySelectorAll(".tools-grid .tool-card").forEach(function (c) {
    c.classList.toggle("hide", cat !== "all" && c.getAttribute("data-cat") !== cat);
  });
}
</script>"""


def _tool_card(href, icon, name, desc, cat):
    return (f'<a class="tool-card" data-cat="{cat}" href="{href}">'
            f'<div class="t-icon">{EMOJI.get(icon, EMOJI["doc"])}</div>'
            f'<h3>{name}</h3><p>{desc}</p></a>')


def _pills(cats):
    btns = ["<button class=\"active\" onclick=\"filterTools('all', this)\">All</button>"]
    for key, label in cats:
        btns.append(f"<button onclick=\"filterTools('{key}', this)\">{label}</button>")
    return '<div class="cat-pills">' + "".join(btns) + "</div>"


def _tools_grid(tools):
    return '<div class="tools-grid">' + "".join(
        _tool_card(*t) for t in tools) + "</div>"


def home_page() -> str:
    grid = _tools_grid(HOME_TOOLS)
    pills = _pills([("pdf", "PDF Tools"), ("document", "Document AI"),
                    ("career", "Career AI"), ("calc", "Calculators"),
                    ("docs", "HR Documents")])
    body = f"""
<section class="page-hero"><div class="container">
  <h1 style="max-width:760px">Every tool you need for PDF, document,
  HR &amp; career work, in one place</h1>
  <p>30 free PDF tools plus AI superpowers. Merge, split, compress and
  convert PDFs, summarize documents, build resumes, write job descriptions,
  generate letters and do salary math - all in a few clicks, no sign-up
  needed.</p>
</div></section>
<section class="section"><div class="container">
  {pills}
  {grid}
</div></section>
{FILTER_JS}
"""
    return page(
        "AI-powered productivity tools",
        "Nexora: free AI tools for documents, HR and careers - Document AI, Resume Builder, ATS Checker, JD Builder, HR calculators and HR documents.",
        "/",
        body,
    )


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




def career_tool_page(slug: str) -> str:
    spec = CAREER_TOOLS[slug]
    nxt = [["/career/" + s, CAREER_TOOLS[s]["title"]]
           for s in CAREER_NEXT.get(slug, [])]
    nxt.append(["/document-ai", "Document AI"])
    cfg = {
        "slug": slug,
        "title": spec["title"],
        "fields": spec["fields"],
        "source": spec.get("source"),
        "sourceRequired": bool(spec.get("source")) and slug not in ("recruitment-optimizer",),
        "download": bool(spec.get("download")),
        "next": nxt,
    }
    body = (CAREER_BODY
            .replace("__CFG_JSON__", json.dumps(cfg))
            .replace("__TITLE__", spec["title"])
            .replace("__TAGLINE__", spec["tagline"])
            .replace("__BUTTON__", spec["button"]))
    body += premium_section(slug)
    return page(spec["title"], spec["seo"], "/hr-career", body)


def hr_career_page() -> str:
    tools = [t for t in HOME_TOOLS if t[4] != "document"]
    grid = _tools_grid(tools)
    pills = _pills([("career", "Career AI"), ("calc", "Calculators"),
                    ("docs", "HR Documents")])
    body = f"""
<section class="page-hero"><div class="container">
  <h1>Every HR &amp; career tool, in one place</h1>
  <p>Practical AI tools for job seekers and HR teams - resumes, job
  descriptions, letters, documents and salary calculators.</p>
</div></section>
<section class="section"><div class="container">
  {pills}
  {grid}
</div></section>
{FILTER_JS}
"""
    return page("HR & Career", "HR and career AI tools: resume builder, resume analyzer, ATS checker, JD builder, cover letters, offer analysis, HR calculators and HR documents.", "/hr-career", body)


def calculators_page() -> str:
    return page("HR Calculators",
                "Free HR calculators: CTC breakdown, take-home pay, increment, gratuity and notice period for India.",
                "/hr-career", CALC_BODY)


# ----------------------------------------------------------------------
# Phase 9: individual SEO tool pages
# ----------------------------------------------------------------------

CALC_TOOL = '<section class="section">' + CALC_BODY.split('<section class="section">', 1)[1]


SEO_CALC_ORDER = ["ctc-calculator", "salary-calculator", "increment-calculator",
                  "gratuity-calculator", "notice-period-calculator"]




def seo_career_page(seo_slug: str) -> str:
    spec = SEO_CAREER_PAGES[seo_slug]
    tool = CAREER_TOOLS[spec["career"]]
    cfg = {
        "slug": spec["career"],
        "title": spec["h1"],
        "fields": tool["fields"],
        "source": tool.get("source"),
        "sourceRequired": bool(tool.get("source")) and spec["career"] not in ("recruitment-optimizer",),
        "download": bool(tool.get("download")),
    }
    body = (CAREER_BODY
            .replace("__CFG_JSON__", json.dumps(cfg))
            .replace("__TITLE__", spec["h1"])
            .replace("__TAGLINE__", spec["intro"])
            .replace("__BUTTON__", tool["button"]))
    faqs = "".join(f"<h3 style='margin:18px 0 6px'>{q}</h3><p>{a}</p>"
                   for q, a in spec["faqs"])
    body += premium_section(spec["career"])
    body += f"""
<section class="section" style="padding-top:0"><div class="container" style="max-width:780px">
  <div class="card">
    <h2 style="margin-top:0">Common questions</h2>
    {faqs}
  </div>
  <div class="card">
    <h2 style="margin-top:0">More free Nexora tools</h2>
    {_seo_links(seo_slug)}
  </div>
</div></section>"""
    return page(spec["title"], spec["meta"], "", body)


def _seo_links(current: str) -> str:
    items = []
    for slug in SEO_CALC_ORDER:
        if slug == current:
            continue
        spec = SEO_CALC_PAGES[slug]
        items.append(f'<a class="btn ghost" href="/{slug}">{spec["title"]}</a>')
    items.append('<a class="btn ghost" href="/resume-ats-checker">Resume ATS Checker</a>')
    return '<div style="display:flex;flex-wrap:wrap;gap:10px">' + "".join(items) + "</div>"


def seo_calc_page(slug: str) -> str:
    spec = SEO_CALC_PAGES[slug]
    how = "".join(f"<li>{step}</li>" for step in spec["how"])
    faqs = "".join(f"<h3 style='margin:18px 0 6px'>{q}</h3><p>{a}</p>"
                   for q, a in spec["faqs"])
    body = f"""
<section class="page-hero"><div class="container">
  <span class="tag live">Free tool</span>
  <h1 style="margin-top:12px">{spec['h1']}</h1>
  <p>{spec['intro']}</p>
</div></section>
{CALC_TOOL}
<script>pick("{spec['calc']}");document.getElementById("tabs").style.display="none";</script>
<section class="section"><div class="container" style="max-width:780px">
  <div class="card">
    <h2 style="margin-top:0">How it works</h2>
    <ol style="line-height:1.9;color:var(--muted)">{how}</ol>
    <p style="margin-top:14px"><strong>{spec['example']}</strong></p>
  </div>
  <div class="card">
    <h2 style="margin-top:0">Common questions</h2>
    {faqs}
  </div>
  <div class="card">
    <h2 style="margin-top:0">More free Nexora tools</h2>
    {_seo_links(slug)}
  </div>
</div></section>"""
    return page(spec["title"], spec["meta"], "", body)


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
        "title": "📜 Offer Letter",
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
        "title": "📋 Appointment Letter",
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
        "title": "📈 Salary Increment Letter",
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
        "title": "⭐ Promotion Letter",
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
        "title": "🏅 Experience Certificate",
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
        "title": "👋 Relieving Letter",
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
        "title": "\⚠️ Warning Letter",
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
        "title": "🚪 Exit Interview Form",
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
    db_insert_async("documents", {
        "doc_id": doc_id, "name": filename[:200], "kind": parsed["kind"],
        "detail": parsed["detail"][:300], "size_bytes": size,
        "chars": len(text) if text else None})
    db_usage("upload", {"kind": parsed["kind"]})
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
# Free-tier daily limits. Per device/network until sign-in is finished;
# the plan doc (30 Sep 2026) moves counting to per-account after that.
# In-memory counter (fast path); every consumed job is also logged to
# Supabase usage for the record. Limits reset at midnight IST.
# ----------------------------------------------------------------------
DAILY_LIMITS = {"pdf": 5, "ai": 3, "doc": 5}
# Single launch toggle: set LIMITS_ENABLED=on in the Render dashboard
# when we go live. Until then every job passes (friends are testing).
LIMITS_ENABLED = os.environ.get("LIMITS_ENABLED", "off").strip().lower() in ("1", "true", "on", "yes")
DAILY_COUNTER = {}
DAILY_LOCK = threading.Lock()


def _ist_day() -> str:
    from datetime import datetime, timezone, timedelta
    return (datetime.now(timezone.utc) + timedelta(hours=5,
                                                   minutes=30)).strftime("%Y-%m-%d")


def daily_limit_response(request: Request, group: str,
                         label: str) -> JSONResponse | None:
    """None when the job may run (and counts it); a friendly 429 when the
    free daily limit for this group is already used up."""
    if not LIMITS_ENABLED:
        return None
    limit = DAILY_LIMITS.get(group)
    if not limit:
        return None
    ip = request.client.host if request.client else "unknown"
    day = _ist_day()
    key = (group, ip, day)
    with DAILY_LOCK:
        if len(DAILY_COUNTER) > 20000:
            DAILY_COUNTER.clear()
        used = DAILY_COUNTER.get(key, 0)
        if used >= limit:
            return err_response(
                429,
                "That is your " + str(limit) + " free " + label + " for "
                "today. They reset at midnight IST - or go Pro for "
                "unlimited use: /pro")
        DAILY_COUNTER[key] = used + 1
    db_usage("daily:" + group, {"day": day})
    return None


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


# ----------------------------------------------------------------------
# Phase 4: Supabase persistence (optional; no-ops until env vars are set)
# ----------------------------------------------------------------------


def db_ready() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def _db_request(method: str, path: str, payload=None):
    """Minimal PostgREST call using stdlib only. Returns parsed JSON or None."""
    import urllib.request
    import urllib.error
    if not db_ready():
        return None
    url = SUPABASE_URL + "/rest/v1/" + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("apikey", SUPABASE_SERVICE_KEY)
    req.add_header("Authorization", "Bearer " + SUPABASE_SERVICE_KEY)
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=minimal")
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read().decode()
            return json.loads(body) if body else True
    except Exception:
        traceback.print_exc()
        return None


def db_insert(table: str, row: dict):
    return _db_request("POST", table, payload=row)


def db_insert_async(table: str, row: dict) -> None:
    """Fire-and-forget insert so DB slowness never blocks a user request."""
    if not db_ready():
        return
    threading.Thread(target=db_insert, args=(table, row), daemon=True).start()


def db_usage(event: str, meta: dict | None = None) -> None:
    db_insert_async("usage", {"event": event[:60], "meta": meta or {}})


def db_history(doc_id: str | None, action: str,
               input_preview: str = "", output_preview: str = "") -> None:
    db_insert_async("document_history", {
        "doc_id": doc_id,
        "action": action[:60],
        "input_preview": (input_preview or "")[:500],
        "output_preview": (output_preview or "")[:2000],
    })


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


# Phase 5 auth routes ---------------------------------------------------


@app.get("/login", response_class=HTMLResponse)
async def login_page(err: str = "", msg: str = "", next: str = "") -> str:
    next_url = next if (next.startswith("/") and not next.startswith("//")) else ""
    safe_next = (next_url.replace("&", "&amp;").replace('"', "&quot;")
                 .replace("<", "&lt;").replace(">", "&gt;"))
    hidden = ('<input type="hidden" name="next" value="' + safe_next + '">') if next_url else ""
    notices = {
        "rate": "Confirmation emails are temporarily rate-limited. Please wait before trying again; repeated taps will not send another email.",
        "mail": "Confirmation email is not available for this address yet. Please contact the site owner; retrying the same form will not fix it.",
        "confirm": "Please confirm your email using the link in your inbox (check Spam too), then sign in.",
        "exists": "An account may already exist for this address. Try signing in, or check your inbox for a confirmation link.",
        "signup": "Could not create your account right now. Please try later.",
        "1": "Sign-in did not complete. Check your email and password and try again.",
    }
    notice = ('<div class="err" style="margin-bottom:14px">'
              + notices[err] + '</div>') if err in notices else ""
    info = ('<div class="hint" style="margin-bottom:14px;color:var(--accent)">'
            'Account created - check your inbox and confirm your email, then sign in.</div>') if msg == "confirm" else ""
    google_on = False
    if auth_ready():
        st, settings = _auth_call("settings")
        google_on = bool(st == 200 and (settings.get("external") or {}).get("google"))
    gbtn = ('<a class="btn" href="/auth/google" style="width:100%">Continue with Google</a>'
            if google_on else
            '<p class="hint" style="margin:0">Google sign-in is being set up - '
            'use email below for now.</p>')
    return page("Sign in", "Sign in to Nexora with Google or email. Free tools never need an account.",
                "", LOGIN_BODY.replace("__ERR__", notice).replace("__MSG__", info).replace("__GOOGLE__", gbtn).replace("__NEXT__", hidden))


@app.get("/auth/google")
async def auth_google():
    if not auth_ready():
        raise HTTPException(status_code=503, detail="Sign-in is not configured yet.")
    import secrets, hashlib
    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    redirect_to = SITE_URL + "/auth/callback"
    from urllib.parse import quote
    url = (SUPABASE_URL + "/auth/v1/authorize?provider=google"
           "&flow_type=pkce&code_challenge=" + challenge
           + "&code_challenge_method=s256&redirect_to=" + quote(redirect_to, safe=""))
    resp = RedirectResponse(url, status_code=302)
    resp.set_cookie(PKCE_COOKIE, verifier, max_age=600, httponly=True,
                    secure=True, samesite="lax")
    return resp


@app.post("/auth/email")
async def auth_email(request: Request):
    if not auth_ready():
        raise HTTPException(status_code=503, detail="Sign-in is not configured yet.")
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    mode = str(form.get("mode", "login"))
    next_url = str(form.get("next", ""))
    if not (next_url.startswith("/") and not next_url.startswith("//")) or len(next_url) > 200:
        next_url = ""
    if not email or len(password) < 6:
        return RedirectResponse("/login?err=1", status_code=302)
    if mode == "signup":
        status, data = _auth_call("signup", {"email": email, "password": password})
    else:
        status, data = _auth_call("token?grant_type=password",
                                  {"email": email, "password": password})
    if status == 200 and "access_token" in data:
        resp = RedirectResponse(next_url or "/", status_code=302)
        resp.set_cookie(SESSION_COOKIE, _session_value(data),
                        max_age=7 * 24 * 3600, httponly=True, secure=True, samesite="lax")
        return resp
    from urllib.parse import quote
    suffix = ("&next=" + quote(next_url, safe="") if next_url else "")
    if mode == "signup":
        if status in (200, 201) and data.get("id"):
            return RedirectResponse("/login?msg=confirm" + suffix, status_code=302)
        code = str(data.get("error_code") or data.get("code") or "")
        if status == 429 or code in ("over_email_send_rate_limit", "over_request_rate_limit"):
            err = "rate"
        elif code in ("email_address_not_authorized", "email_provider_disabled"):
            err = "mail"
        elif code in ("user_already_exists", "email_exists"):
            err = "exists"
        else:
            err = "signup"
        print("signup failed: status=%s code=%s" % (status, code), flush=True)
        return RedirectResponse("/login?err=" + err + suffix, status_code=302)
    if str(data.get("error_code") or "") in ("email_not_confirmed",):
        return RedirectResponse("/login?err=confirm" + suffix, status_code=302)
    return RedirectResponse("/login?err=1" + suffix, status_code=302)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code", "")
    verifier = request.cookies.get(PKCE_COOKIE, "")
    if not code or not verifier or not auth_ready():
        return RedirectResponse("/login?err=1", status_code=302)
    status, tokens = _auth_call("token?grant_type=pkce", {
        "auth_code": code,
        "code_verifier": verifier,
        "redirect_uri": SITE_URL + "/auth/callback",
    })
    if status != 200 or "access_token" not in tokens:
        return RedirectResponse("/login?err=1", status_code=302)
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(SESSION_COOKIE, _session_value(tokens),
                    max_age=7 * 24 * 3600, httponly=True, secure=True, samesite="lax")
    resp.delete_cookie(PKCE_COOKIE, path="/")
    return resp


@app.get("/auth/logout")
async def auth_logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp


@app.get("/api/me")
async def api_me(request: Request):
    payload, expired = _load_session(request)
    if not payload:
        return JSONResponse({"authenticated": False})
    refreshed_cookie = None
    if expired and payload.get("rt"):
        status, tokens = _auth_call("token?grant_type=refresh_token",
                                    {"refresh_token": payload["rt"]})
        if status == 200 and "access_token" in tokens:
            payload = {"at": tokens["access_token"],
                       "rt": tokens.get("refresh_token", payload["rt"]),
                       "exp": int(time.time()) + int(tokens.get("expires_in", 3600)) - 120}
            refreshed_cookie = _session_value(tokens)
        else:
            return JSONResponse({"authenticated": False})
    status, user = _auth_call("user", token=payload["at"])
    if status != 200:
        return JSONResponse({"authenticated": False})
    meta = user.get("user_metadata") or {}
    name = meta.get("full_name") or meta.get("name") or ""
    out = JSONResponse({"authenticated": True,
                        "email": user.get("email", ""), "name": name})
    if refreshed_cookie:
        out.set_cookie(SESSION_COOKIE, refreshed_cookie,
                       max_age=7 * 24 * 3600, httponly=True,
                       secure=True, samesite="lax")
    return out


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "nexora"})


PRO_BODY = r"""
<section class="hero">
  <div class="container">
    <span class="pill pill-soft">Early access</span>
    <h1>Nexora Pro</h1>
    <p class="lead">Every tool, unlimited. No daily caps, bigger files,
    batch jobs and priority speed - for the price of one movie ticket a
    month.</p>
  </div>
</section>
<section class="section">
  <div class="container grid-2">
    <div class="card">
      <h3>Free</h3>
      <p class="price">&#8377;0 <span>/ forever</span></p>
      <p>All 45 tools, every day: 5 PDF jobs, 3 AI runs and 5 documents
      per day, files up to 25 MB. No sign-up needed.</p>
    </div>
    <div class="card">
      <h3>Pro <span class="tag pro">Launch offer</span></h3>
      <p class="price">&#8377;149 <span>/ month</span></p>
      <p>Unlimited jobs, files up to 100 MB, batch processing and
      priority speed. Pay by UPI in ten seconds. First month
      &#8377;99 for early users.</p>
      <p style="margin-top:16px"><button class="btn" disabled
        style="opacity:.6;cursor:not-allowed">Checkout opens soon</button></p>
      <p style="margin-top:10px;font-size:14px;color:var(--ink-2,#666)">
      UPI checkout is being finished and tested. Until it opens,
      everything stays free with the daily limits above - no card
      needed, nothing to cancel.</p>
    </div>
  </div>
</section>
"""


@app.get("/pro", response_class=HTMLResponse)
async def pro_page() -> str:
    return page("Nexora Pro - unlimited tools, one small price",
                "Nexora Pro: unlimited PDF and AI tools, bigger files, "
                "batch jobs and priority speed for one small monthly price.",
                "/pro", PRO_BODY)


# Online resume/document service. No street address, coordinates or LocalBusiness schema.
RESUME_SERVICE_WHATSAPP = "https://wa.me/919353006448?text=Namaskara%21+I+found+Nexora%27s+resume+and+document+formatting+page.+I%27d+like+a+quote.+Document+type%3A%0AChanges+needed%3A%0ADeadline%3A"


def resume_service_page() -> str:
    body = """
<style>
.rs-hero{padding:56px 0 34px;background:linear-gradient(135deg,#faf5ff,#fff1f9)}
.rs-layout{display:grid;grid-template-columns:1.25fr 1fr;gap:32px;align-items:center}
.rs-hero h1{font-size:clamp(32px,5vw,54px);line-height:1.12;margin:16px 0}
.rs-hero p{font-size:18px;max-width:650px;line-height:1.65}
.rs-label{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#7c3aed}
.rs-paper{background:white;border:1px solid #eee1f6;border-radius:20px;padding:30px;box-shadow:0 16px 48px #7c3aed12}
.rs-paper h2{font-size:22px;margin:0 0 6px}.rs-paper small{color:#6b7280}
.rs-line{height:9px;background:#ede9fe;border-radius:8px;margin-top:14px}.rs-line.short{width:62%}
.rs-paper hr{border:0;border-top:2px solid #a78bfa;margin:22px 0}
.rs-section{padding:36px 0}.rs-section h2{font-size:28px;margin:0 0 16px}
.rs-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.rs-box{background:white;border:1px solid #eee5f3;border-radius:16px;padding:24px}
.rs-box h3{margin:0 0 10px;font-size:19px}.rs-box p{line-height:1.65;margin:0;color:#5b5263}
.rs-note{background:#faf5ff;border-radius:14px;padding:22px;line-height:1.7}
.rs-faq details{border-bottom:1px solid #eee5f3;padding:16px 0}.rs-faq summary{font-weight:650;cursor:pointer}.rs-faq p{line-height:1.7;color:#5b5263}
.rs-actions{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 12px}.rs-actions a{min-height:48px;display:inline-flex;align-items:center}
.rs-small{font-size:14px!important;color:#6b7280}
@media(max-width:700px){.rs-layout,.rs-grid{grid-template-columns:1fr}.rs-hero{padding:30px 0}.rs-paper{display:none}.rs-section{padding:26px 0}.rs-actions a{width:100%;justify-content:center}.rs-box{padding:20px}}
</style>
<section class="rs-hero"><div class="container rs-layout"><div>
<span class="rs-label">Nexora / Online document help</span>
<h1>A clean resume.<br>A simpler next step.</h1>
<p>Resume formatting and Word/PDF document cleanup, handled online through WhatsApp. No shop visit or physical meeting needed.</p>
<div class="rs-actions"><a class="btn" href="__WHATSAPP__" rel="noopener noreferrer">Ask for a quote on WhatsApp</a><a class="btn ghost" href="/resume-builder">Try the resume builder</a></div>
<p class="rs-small">Price and delivery time agreed before work starts. No payment is taken on this page.</p>
</div><div class="rs-paper" aria-label="Illustrative resume layout"><h2>Your name</h2><small>Clear structure. Consistent formatting.</small><hr><strong>Profile</strong><div class="rs-line"></div><div class="rs-line short"></div><br><strong>Experience &amp; skills</strong><div class="rs-line"></div><div class="rs-line"></div><div class="rs-line short"></div><p class="rs-small">Illustrative layout, not a customer resume.</p></div></div></section>
<section class="rs-section"><div class="container"><h2>What you can request</h2><div class="rs-grid">
<article class="rs-box"><h3>Resume formatting</h3><p>A clearer layout for your existing resume: consistent headings, spacing, fonts and sections. Suitable for freshers and experienced applicants.</p></article>
<article class="rs-box"><h3>Word document cleanup</h3><p>Fix uneven spacing, headings, page breaks and alignment in an existing Word document. Send a short description of the changes you need.</p></article>
<article class="rs-box"><h3>PDF preparation</h3><p>Prepare a readable PDF from your document. Tell us whether you also need the editable Word file, and we will confirm what can be delivered.</p></article>
</div></div></section>
<section class="rs-section"><div class="container"><h2>From first message to final file</h2><div class="rs-grid">
<article class="rs-box"><h3>1. Tell us what you need</h3><p>Message on WhatsApp with the document type, requested changes and deadline. A redacted sample is enough to start a quote.</p></article>
<article class="rs-box"><h3>2. Agree the scope</h3><p>Confirm the price, delivery date and file format before work starts. Ask what changes are included.</p></article>
<article class="rs-box"><h3>3. Review your file</h3><p>Check the finished document, names and facts before using it. Formatting does not change or verify your qualifications.</p></article>
</div></div></section>
<section class="rs-section"><div class="container"><div class="rs-note"><strong>Share only what is needed.</strong><br>Share only the information needed for the document. Please remove Aadhaar/PAN numbers, bank details and other sensitive data. Never send passwords or OTPs. This service is fully online; no home address or meeting location is published here.</div></div></section>
<section class="rs-section"><div class="container rs-faq"><h2>Before you message</h2>
<details><summary>How much does it cost?</summary><p>Request a quote for your document. The price depends on the work and is agreed before starting. There is no published fixed price or automatic charge.</p></details>
<details><summary>Do I need to meet someone?</summary><p>No. Requests and delivery are handled online through WhatsApp. No in-person appointments are offered.</p></details>
<details><summary>Will this guarantee an interview or ATS score?</summary><p>No. This is a formatting and document-cleanup service, not recruitment or a job guarantee. Hiring decisions and ATS systems vary.</p></details>
<details><summary>Can I use Nexora myself instead?</summary><p>Yes. Try the <a href="/resume-builder">resume builder</a>, <a href="/resume-ats-checker">resume ATS checker</a> and <a href="/hr-career">HR and career tools</a>. Tool limits and any paid options are shown separately in the app.</p></details>
<div class="rs-actions"><a class="btn" href="__WHATSAPP__" rel="noopener noreferrer">Discuss your document on WhatsApp</a></div>
</div></section>
""".replace("__WHATSAPP__", RESUME_SERVICE_WHATSAPP)
    html = page("Online resume formatting & document cleanup", "Get help formatting your resume and cleaning up Word/PDF documents online through WhatsApp. Agree a quote and delivery date before starting. No physical meetings.", "/resume-service", body)
    metadata = '<link rel="canonical" href="https://nexora-web-q7rn.onrender.com/resume-service"><meta name="robots" content="index,follow"><meta property="og:title" content="Online resume formatting - Nexora"><meta property="og:description" content="Resume and document formatting, fully online. Ask for a quote before work starts."><meta property="og:url" content="https://nexora-web-q7rn.onrender.com/resume-service"><meta property="og:type" content="website">'
    return html.replace("</head>", metadata + "</head>")


@app.get("/resume-service", response_class=HTMLResponse)
async def resume_service_landing() -> str:
    return resume_service_page()


@app.get("/robots.txt")
async def robots_txt() -> Response:
    return Response("User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /auth/\nSitemap: https://nexora-web-q7rn.onrender.com/sitemap.xml\n", media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap_xml() -> Response:
    paths = ["/", "/privacy", "/terms", "/resume-service", "/document-ai", "/hr-career", "/resume-builder", "/jd-builder", "/hr/calculators", "/hr/documents"]
    paths += ["/" + slug for slug in SEO_CALC_PAGES] + ["/" + slug for slug in SEO_CAREER_PAGES]
    urls = "".join("<url><loc>https://nexora-web-q7rn.onrender.com" + path + "</loc></url>" for path in dict.fromkeys(paths))
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>', media_type="application/xml")



def legal_page(kind: str) -> str:
    privacy = """
<h1>Privacy policy</h1><p class="legal-date">Updated 30 September 2026</p>
<p>Nexora provides document, PDF, HR and career tools and an online document-formatting service. This page explains the current handling of information on this website.</p>
<h2>Information you provide</h2><p>Tools process files, document text, form answers and chat questions you submit. If you sign in with Google, Supabase authentication receives account information such as your email address and name and manages your user ID and authentication tokens. The website uses cookies for sign-in sessions and the Google sign-in flow.</p>
<h2>Processing and service providers</h2><p>AI requests send the relevant document content, prompts or images to Google Gemini to produce a response. Supabase provides authentication and database storage. Render hosts the website. These services handle information under their own terms and privacy policies. Do not upload passwords, payment-card details, identity-document numbers or confidential material you do not have permission to share.</p>
<h2>What is retained</h2><p>Uploaded documents and extracted content are held in the server's memory. The app checks for documents older than six hours when another upload happens, and can also remove older documents when its memory limit is reached. A server restart may remove them earlier. This is not a guaranteed six-hour deletion schedule.</p><p>When database storage is configured, Supabase stores document metadata (such as filename, type and size), input previews up to 500 characters and output previews up to 2,000 characters, chat questions up to 2,000 characters and replies up to 4,000 characters, usage records, and payment or purchase history where those features are used. These records can outlast the temporary in-memory documents. No fixed automatic deletion period is currently promised for database records.</p>
<h2>WhatsApp document help</h2><p>The document-help button opens WhatsApp. Information or files you send there are handled separately from website uploads and are used to discuss and carry out your request. Ask about handling and deletion before sending sensitive documents. WhatsApp is governed by its own privacy policy.</p>
<h2>Your choices and contact</h2><p>Share only what a task needs, remove sensitive details where possible, and review AI outputs before using them. For questions or requests about access, correction or deletion, email <a href="mailto:a.dennisasw@gmail.com">a.dennisasw@gmail.com</a>. Requests are reviewed according to available records and applicable requirements; this page does not promise instant deletion from every provider or backup.</p>
"""
    terms = """
<h1>Terms of use</h1><p class="legal-date">Updated 30 September 2026</p>
<p>These terms apply to Nexora's document, PDF, HR and career tools and the online document-formatting service. Please read the <a href="/privacy">privacy policy</a> before submitting information.</p>
<h2>Use your own or authorized material</h2><p>Only upload documents and information you have permission to use and process. Do not use Nexora for unlawful activity, misleading qualifications, harmful content or attempts to access other people's accounts or files.</p>
<h2>Review the results</h2><p>AI outputs can be incomplete or wrong. Check names, facts, calculations, formatting and suitability before relying on a result. Nexora is not a recruitment agency and does not guarantee interviews, jobs, ATS scores or other outcomes. Outputs are not legal, financial or professional advice.</p>
<h2>Availability and limits</h2><p>The website uses free-tier hosting and other external services. It may be slow after inactivity, unavailable or subject to file-size, usage and service limits. Features can change. Keep copies of your original files and download results you need; Nexora is not a permanent document-storage service.</p>
<h2>Paid options and online document help</h2><p>Any paid tool must show its price and purchase details before payment. Check those details before approving a purchase. For WhatsApp document help, agree the scope, price, delivery date, file format, included revisions and cancellation or refund arrangements before work begins. This service is fully online and does not offer physical meetings. The landing page itself does not take payment.</p>
<h2>Accounts and third-party services</h2><p>Keep your account secure and do not share passwords or verification codes. Google, Supabase, Render, Gemini, WhatsApp and any payment provider may apply their own terms to their services. Nexora does not promise uninterrupted operation or error-free results. Nothing on this page removes rights that apply under law.</p>
<h2>Contact</h2><p>For service questions or concerns, email <a href="mailto:a.dennisasw@gmail.com">a.dennisasw@gmail.com</a>. Check this page for updates before using the service.</p>
"""
    title = "Privacy policy" if kind == "privacy" else "Terms of use"
    content = privacy if kind == "privacy" else terms
    body = '<style>.legal-wrap{max-width:850px;margin:auto;padding:42px 22px 56px}.legal-wrap h1{font-size:clamp(30px,5vw,44px);line-height:1.2}.legal-wrap h2{font-size:23px;margin:30px 0 10px}.legal-wrap p{line-height:1.8;margin:12px 0}.legal-wrap a{overflow-wrap:anywhere}.legal-date{color:#6b7280;font-size:14px}</style><section class="legal-wrap">' + content + '</section>'
    return page(title, title + " for Nexora document and career tools.", "/" + kind, body)


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy() -> str:
    return legal_page("privacy")


@app.get("/terms", response_class=HTMLResponse)
async def terms_of_use() -> str:
    return legal_page("terms")


@app.get("/{seo_slug}", response_class=HTMLResponse)
async def seo_tool_page(seo_slug: str) -> HTMLResponse:
    if seo_slug in SEO_CALC_PAGES:
        return HTMLResponse(seo_calc_page(seo_slug))
    if seo_slug in SEO_CAREER_PAGES:
        return HTMLResponse(seo_career_page(seo_slug))
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/hr/documents", response_class=HTMLResponse)
async def hr_documents() -> str:
    return hr_documents_page()


# ----------------------------------------------------------------------
# PDF Tools: 30 self-hosted utilities (pdf_tools.py)
# ----------------------------------------------------------------------

PDF_TOOL_MAX_BYTES = 25 * 1024 * 1024  # 25 MB total per request



# ----------------------------------------------------------------------
# Post-task success panel: "Continue to..." suggestions and share phrases
# ----------------------------------------------------------------------

PDF_NEXT = {
    "merge": ["split", "compress", "pdf-to-word", "organize", "protect"],
    "split": ["merge", "extract-images", "compress", "organize", "rotate"],
    "compress": ["merge", "grayscale", "repair", "split", "pdf-to-word"],
    "pdf-to-word": ["pdf-to-excel", "pdf-to-ppt", "word-to-pdf", "pdf-to-txt", "edit"],
    "word-to-pdf": ["excel-to-pdf", "ppt-to-pdf", "merge", "compress", "protect"],
    "pdf-to-ppt": ["pdf-to-word", "pdf-to-excel", "ppt-to-pdf", "pdf-to-jpg", "merge"],
    "ppt-to-pdf": ["word-to-pdf", "excel-to-pdf", "merge", "pdf-to-ppt", "compress"],
    "pdf-to-excel": ["pdf-to-word", "pdf-to-txt", "excel-to-pdf", "split", "merge"],
    "excel-to-pdf": ["word-to-pdf", "pdf-to-excel", "merge", "compress", "protect"],
    "pdf-to-jpg": ["extract-images", "jpg-to-pdf", "pdf-to-word", "compress", "split"],
    "jpg-to-pdf": ["scan-to-pdf", "pdf-to-jpg", "compress", "merge", "watermark"],
    "edit": ["sign", "watermark", "page-numbers", "merge", "protect"],
    "sign": ["protect", "watermark", "edit", "merge", "pdf-to-word"],
    "watermark": ["protect", "sign", "page-numbers", "merge", "compress"],
    "rotate": ["organize", "crop", "merge", "split", "page-numbers"],
    "html-to-pdf": ["word-to-pdf", "jpg-to-pdf", "merge", "compress", "protect"],
    "unlock": ["protect", "merge", "split", "compress", "repair"],
    "protect": ["unlock", "watermark", "sign", "merge", "compress"],
    "organize": ["merge", "split", "rotate", "page-numbers", "extract-images"],
    "repair": ["compress", "unlock", "split", "merge", "pdf-to-word"],
    "page-numbers": ["watermark", "organize", "rotate", "merge", "sign"],
    "scan-to-pdf": ["jpg-to-pdf", "ocr", "compress", "merge", "edit"],
    "ocr": ["pdf-to-word", "pdf-to-txt", "scan-to-pdf", "pdf-to-markdown", "compress"],
    "compare": ["redact", "organize", "split", "merge", "pdf-to-word"],
    "redact": ["protect", "watermark", "compare", "merge", "sign"],
    "crop": ["rotate", "organize", "compress", "merge", "split"],
    "pdf-to-markdown": ["pdf-to-txt", "pdf-to-word", "ocr", "split", "extract-images"],
    "pdf-to-txt": ["pdf-to-markdown", "pdf-to-word", "ocr", "extract-images", "split"],
    "extract-images": ["pdf-to-jpg", "split", "compress", "jpg-to-pdf", "pdf-to-word"],
    "grayscale": ["compress", "watermark", "merge", "rotate", "pdf-to-word"],
}

PDF_SHARE = {
    "merge": "merged my PDFs",
    "split": "split a PDF",
    "compress": "compressed a PDF",
    "pdf-to-word": "turned a PDF into Word",
    "word-to-pdf": "turned a Word file into a PDF",
    "pdf-to-ppt": "turned a PDF into slides",
    "ppt-to-pdf": "turned slides into a PDF",
    "pdf-to-excel": "pulled a PDF table into Excel",
    "excel-to-pdf": "turned a spreadsheet into a PDF",
    "pdf-to-jpg": "turned PDF pages into images",
    "jpg-to-pdf": "turned photos into a PDF",
    "edit": "edited a PDF online",
    "sign": "signed a PDF online",
    "watermark": "watermarked a PDF",
    "rotate": "rotated a PDF",
    "html-to-pdf": "saved a webpage as a PDF",
    "unlock": "unlocked a PDF",
    "protect": "password-protected a PDF",
    "organize": "reorganized PDF pages",
    "repair": "repaired a broken PDF",
    "page-numbers": "added page numbers to a PDF",
    "scan-to-pdf": "turned phone photos into a clean PDF scan",
    "ocr": "made a scanned PDF searchable",
    "compare": "compared two PDFs",
    "redact": "blacked out sensitive text in a PDF",
    "crop": "cropped a PDF",
    "pdf-to-markdown": "turned a PDF into Markdown",
    "pdf-to-txt": "pulled text out of a PDF",
    "extract-images": "pulled images out of a PDF",
    "grayscale": "made a PDF print-friendly",
}

CAREER_NEXT = {
    "resume-builder": ["ats-optimizer", "resume-analyzer", "cover-letter-builder", "offer-letter-analyzer"],
    "resume-analyzer": ["ats-optimizer", "resume-builder", "cover-letter-builder", "jd-analyzer"],
    "ats-optimizer": ["resume-builder", "resume-analyzer", "cover-letter-builder", "jd-builder"],
    "jd-builder": ["jd-analyzer", "recruitment-optimizer", "cover-letter-builder", "ats-optimizer"],
    "jd-analyzer": ["jd-builder", "recruitment-optimizer", "ats-optimizer", "resume-analyzer"],
    "recruitment-optimizer": ["jd-builder", "jd-analyzer", "ats-optimizer", "resume-analyzer"],
    "cover-letter-builder": ["resume-builder", "ats-optimizer", "offer-letter-analyzer", "jd-analyzer"],
    "offer-letter-analyzer": ["resume-analyzer", "cover-letter-builder", "jd-analyzer", "ats-optimizer"],
}

def pdf_tool_page(slug: str) -> str:
    spec = PDF_TOOL_SPECS.get(slug)
    if not spec:
        raise HTTPException(status_code=404, detail="Not found")
    cfg = {
        "slug": slug,
        "title": spec["title"],
        "multiple": bool(spec["multiple"]),
        "options": spec["options"],
        "next": [["/pdf/" + s, PDF_TOOL_SPECS[s]["title"]]
                 for s in PDF_NEXT.get(slug, [])],
        "share": ("I just " + PDF_SHARE[slug] + " with Nexora - free, no sign-up. Try it: ")
                 if slug in PDF_SHARE else None,
    }
    hint = "Accepted: " + spec["accept"]
    if spec["multiple"]:
        hint += " - you can add several files"
    if spec.get("extra_file"):
        hint += ". " + spec["extra_file"]
    body = (PDF_TOOL_BODY
            .replace("__TITLE__", spec["title"])
            .replace("__DESC__", spec["desc"])
            .replace("__ACCEPT__", spec["accept"])
            .replace("__MULTI__", "multiple" if spec["multiple"] else "")
            .replace("__HINT__", hint)
            .replace("__CFG_JSON__", json.dumps(cfg))
            .replace("__UPLOAD_ICON__", ICONS["upload"]))
    return page(spec["title"],
                spec["title"] + " - free online, no sign-up. " + spec["desc"],
                "/", body)


@app.get("/pdf/{slug}", response_class=HTMLResponse)
async def pdf_tool(slug: str) -> str:
    return pdf_tool_page(slug)


@app.post("/api/pdf/{slug}")
async def api_pdf_tool(request: Request, slug: str) -> Response:
    from starlette.concurrency import run_in_threadpool
    if slug not in PDF_TOOL_SPECS:
        raise HTTPException(status_code=404, detail="Not found")
    ip = request.client.host if request.client else "unknown"
    if not rate_ok(ip):
        return err_response(429, "Too many requests. Please wait a while and try again.")
    limited = daily_limit_response(request, "pdf", "PDF jobs")
    if limited:
        return limited
    form = await request.form()
    files = []
    total = 0
    for f in form.getlist("files"):
        blob = await f.read()
        if not blob:
            continue
        total += len(blob)
        if total > PDF_TOOL_MAX_BYTES:
            return err_response(400, "Those files together are larger than 25 MB. "
                                     "Please use smaller files.")
        files.append((os.path.basename(f.filename or "file")[:120], blob))
    opts = {k: str(v)[:500] for k, v in form.items() if k != "files"}
    try:
        data, fname, mime = await run_in_threadpool(run_tool, slug, files, opts)
    except ToolError as e:
        msg = str(e)
        if msg == "ocr-unavailable":
            msg = ("The OCR engine is being enabled on the server. "
                   "Please try again shortly.")
        return err_response(400, msg)
    except Exception:
        traceback.print_exc()
        return err_response(500, "That file could not be processed. Please try another one.")
    db_usage("pdf_tool", {"tool": slug})
    db_history(None, "pdf_tool:" + slug)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", fname)
    return Response(content=data, media_type=mime,
                    headers={"Content-Disposition": 'attachment; filename="' + safe + '"'})



# ----------------------------------------------------------------------
# Document AI API
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Phase 6+7: Razorpay payments and secure paid-feature unlocking.
# Inert until RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET are set in Render.
# Flow: login -> /api/pay/order -> Razorpay checkout -> /api/pay/verify
# (server-side HMAC check) -> purchases credit -> /api/premium/{product}
# re-checks the credit server-side before any AI run. Never trust client.
# ----------------------------------------------------------------------

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "").strip()
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()

PAID_PRODUCTS = {
    "resume_improve": {
        "name": "AI Resume Improvement",
        "blurb": "Your whole resume rewritten by AI - stronger wording, quantified achievements, ATS-optimized - as an editable Word file.",
        "price_paise": 9900,
        "source_label": "your current resume",
        "prompt": (
            "You are a senior resume writer and ATS specialist. Rewrite this resume "
            "into a complete, improved, ATS-optimized version. Keep every true fact; "
            "strengthen wording, quantify achievements where the source implies them, "
            "fix structure and ordering, and add a short professional summary. "
            "Output the full improved resume in clean markdown, then a short "
            "'What changed and why' section with 5-8 bullets. Target role (if any): {target}"),
    },
    "jd_improve": {
        "name": "AI JD Improvement",
        "blurb": "The complete improved JD - restructured, bias-free, realistic requirements - ready to post, as an editable Word file.",
        "price_paise": 14900,
        "source_label": "your job description",
        "prompt": (
            "You are a senior HR consultant. Rewrite this job description into a "
            "complete, improved version: clear structure (about the role, "
            "responsibilities, must-have vs nice-to-have skills, benefits, how to "
            "apply), inclusive and bias-free language, realistic requirements, and "
            "a compelling but honest tone. Output the full improved JD in clean "
            "markdown, then a short 'What changed and why' section with 5-8 bullets. "
            "Company context (if any): {target}"),
    },
    "offer_review": {
        "name": "Full Offer Letter Review",
        "blurb": "Every clause explained in plain English, red flags flagged, and exact negotiation wording you can send - as an editable Word file.",
        "price_paise": 9900,
        "source_label": "your offer letter",
        "prompt": (
            "You are an expert compensation and employment advisor in India. Give a "
            "full review of this offer letter: (1) plain-English explanation of every "
            "clause, (2) red flags and risky terms with why they matter, (3) "
            "compensation breakdown sanity check (CTC vs in-hand, variable, joining "
            "bonus, bond/notice clauses), (4) specific negotiation points with exact "
            "wording the candidate can send, (5) questions to ask before signing. "
            "Be concrete and specific to this letter, not generic. Candidate's "
            "concerns (if any): {target}"),
    },
    "cover_letter_pro": {
        "name": "Professional Cover Letter",
        "blurb": "A polished, ready-to-send cover letter matched to the job and your real experience - as an editable Word file.",
        "price_paise": 7900,
        "source_label": "the job description (and your resume if you have it)",
        "prompt": (
            "You are a professional cover-letter writer. Write a polished, specific, "
            "ready-to-send cover letter based on the material provided. Match the "
            "candidate's real experience to the role's actual requirements, keep it "
            "under 350 words, no clichés, confident warm tone, and end with a clear "
            "call to action. Output only the letter, ready to paste. "
            "Anything to emphasize (if any): {target}"),
    },
}


TOOL_PRODUCT = {
    "resume-builder": "resume_improve",
    "resume-analyzer": "resume_improve",
    "ats-optimizer": "resume_improve",
    "jd-builder": "jd_improve",
    "jd-analyzer": "jd_improve",
    "offer-letter-analyzer": "offer_review",
    "cover-letter-builder": "cover_letter_pro",
}


def premium_section(career_slug: str) -> str:
    product = TOOL_PRODUCT.get(career_slug)
    if not product:
        return ""
    spec = PAID_PRODUCTS[product]
    cfg = json.dumps({
        "product": product, "name": spec["name"], "blurb": spec["blurb"],
        "price": spec["price_paise"] // 100,
        "sourceLabel": spec["source_label"]})
    return PREMIUM_BODY.replace("__PCFG__", cfg)


def payments_ready() -> bool:
    # Fail closed. Keys alone must never expose checkout. Enable only after the
    # schema, order persistence, verification, credit grants and consumption
    # have been tested end-to-end. Keep PAYMENTS_ENABLED unset until then.
    return bool(os.environ.get("PAYMENTS_ENABLED", "").lower() == "true"
                and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and db_ready())


def _current_user(request: Request):
    """Return the Supabase auth user dict (has 'id' and 'email') or None."""
    if not auth_ready():
        return None
    payload, expired = _load_session(request)
    if not payload:
        return None
    if expired:
        rt = payload.get("rt")
        if not rt:
            return None
        status, tokens = _auth_call("token?grant_type=refresh_token",
                                    {"refresh_token": rt})
        if status != 200 or "access_token" not in tokens:
            return None
        payload = {"at": tokens["access_token"]}
    status, user = _auth_call("user", token=payload["at"])
    if status != 200 or not isinstance(user, dict) or not user.get("id"):
        return None
    return user


def _rzp_call(path: str, payload: dict):
    """POST to the Razorpay REST API with basic auth. Returns (status, json)."""
    import urllib.request
    import urllib.error
    import base64
    url = "https://api.razorpay.com/v1/" + path
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    cred = base64.b64encode(
        (RAZORPAY_KEY_ID + ":" + RAZORPAY_KEY_SECRET).encode()).decode()
    req.add_header("Authorization", "Basic " + cred)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception:
        traceback.print_exc()
        return 0, {}


def _verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    import hmac
    import hashlib
    expect = hmac.new(RAZORPAY_KEY_SECRET.encode(),
                      (order_id + "|" + payment_id).encode(),
                      hashlib.sha256).hexdigest()
    return hmac.compare_digest(expect, signature or "")


def _payment_row(order_id: str):
    rows = _db_request("GET", "payments?razorpay_order_id=eq." + order_id
                       + "&select=*")
    return rows[0] if isinstance(rows, list) and rows else None


@app.post("/api/pay/order")
async def api_pay_order(request: Request):
    if not payments_ready():
        return err_response(503, "Payments are being set up. Please check back soon.")
    if not db_ready():
        return err_response(503, "Payments are being set up. Please check back soon.")
    user = _current_user(request)
    if not user:
        return JSONResponse({"error": "Please sign in to continue.", "login": True},
                            status_code=401)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    product = str(payload.get("product") or "") if isinstance(payload, dict) else ""
    spec = PAID_PRODUCTS.get(product)
    if not spec:
        return err_response(404, "Unknown product.")
    receipt = "nx_" + uuid.uuid4().hex[:16]
    status, order = _rzp_call("orders", {
        "amount": spec["price_paise"],
        "currency": "INR",
        "receipt": receipt,
        "notes": {"product": product, "email": user.get("email", "")},
    })
    if status not in (200, 201) or not order.get("id"):
        return err_response(502, "Could not start the payment. Please try again.")
    db_insert("payments", {
        "user_id": user["id"],
        "razorpay_order_id": order["id"],
        "amount_paise": spec["price_paise"],
        "currency": "INR",
        "status": "created",
        "product": product,
    })
    return JSONResponse({
        "order_id": order["id"], "amount": spec["price_paise"],
        "currency": "INR", "key_id": RAZORPAY_KEY_ID,
        "product": product, "name": spec["name"],
        "email": user.get("email", "")})


@app.post("/api/pay/verify")
async def api_pay_verify(request: Request):
    if not payments_ready() or not db_ready():
        return err_response(503, "Payments are being set up. Please check back soon.")
    user = _current_user(request)
    if not user:
        return JSONResponse({"error": "Please sign in to continue.", "login": True},
                            status_code=401)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    order_id = str(payload.get("razorpay_order_id") or "")
    payment_id = str(payload.get("razorpay_payment_id") or "")
    signature = str(payload.get("razorpay_signature") or "")
    if not (order_id and payment_id and signature):
        return err_response(400, "Missing payment details.")
    row = _payment_row(order_id)
    if not row or row.get("user_id") != user["id"]:
        return err_response(404, "Unknown order.")
    if row.get("status") == "verified":
        return JSONResponse({"ok": True, "product": row.get("product"),
                             "already": True})
    if not _verify_signature(order_id, payment_id, signature):
        _db_request("PATCH", "payments?razorpay_order_id=eq." + order_id,
                    {"status": "failed"})
        return err_response(400, "Payment could not be verified. If any money was "
                            "deducted, Razorpay refunds it automatically.")
    _db_request("PATCH", "payments?razorpay_order_id=eq." + order_id,
                {"status": "verified", "razorpay_payment_id": payment_id})
    db_insert("purchases", {"user_id": user["id"],
                            "product": row.get("product") or "",
                            "unlocked": True})
    db_usage("purchase", {"product": row.get("product")})
    return JSONResponse({"ok": True, "product": row.get("product")})


@app.post("/api/premium/{product}")
async def api_premium(product: str, request: Request):
    spec = PAID_PRODUCTS.get(product)
    if not spec:
        return err_response(404, "Unknown product.")
    if not db_ready():
        return err_response(503, "This feature is being set up. Please check back soon.")
    if not gemini_ready():
        return err_response(503, "The AI engine is being configured. Please try again shortly.")
    user = _current_user(request)
    if not user:
        return JSONResponse({"error": "Please sign in to continue.", "login": True},
                            status_code=401)
    credits = _db_request("GET", "purchases?user_id=eq." + user["id"]
                          + "&product=eq." + product
                          + "&unlocked=eq.true&select=id&limit=1")
    if not (isinstance(credits, list) and credits):
        return JSONResponse({"error": "This feature needs a one-time payment.",
                             "pay_required": True, "product": product,
                             "name": spec["name"],
                             "price_paise": spec["price_paise"]}, status_code=402)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    source_text = str(payload.get("source_text") or "")[:30000].strip()
    doc_id = str(payload.get("doc_id") or "").strip()
    if doc_id and not source_text:
        doc, err = doc_or_404(doc_id)
        if err:
            return err
        source_text = doc.get("text", "")[:30000]
    if len(source_text) < 40:
        return err_response(400, "Please paste " + spec["source_label"] + " first.")
    fields = {"target": str(payload.get("target") or "")[:500]}
    # Consume the credit before the AI run so a double-click cannot spend it twice.
    _db_request("PATCH", "purchases?id=eq." + str(credits[0]["id"]),
                {"unlocked": False})
    try:
        out = gemini_generate({"name": spec["name"], "text": source_text,
                               "raw": None},
                              spec["prompt"].format_map(_F(fields)))
    except Exception:
        traceback.print_exc()
        # AI failed - give the credit back.
        _db_request("PATCH", "purchases?id=eq." + str(credits[0]["id"]),
                    {"unlocked": True})
        return err_response(502, "The AI could not process this right now. "
                            "Your credit was not used - please try again.")
    db_history(doc_id or None, "premium:" + product,
               input_preview=source_text[:500], output_preview=out)
    db_usage("premium:" + product)
    return JSONResponse({"result": out})


@app.get("/api/purchases")
async def api_purchases(request: Request):
    user = _current_user(request)
    if not user:
        return JSONResponse({"authenticated": False, "purchases": []})
    rows = _db_request("GET", "purchases?user_id=eq." + user["id"]
                       + "&select=product,unlocked,created_at"
                       + "&order=created_at.desc&limit=50")
    return JSONResponse({"authenticated": True,
                         "purchases": rows if isinstance(rows, list) else []})


@app.get("/api/config")
async def api_config() -> JSONResponse:
    return JSONResponse({"ai_ready": gemini_ready(), "db_ready": db_ready(),
                        "auth_ready": auth_ready(),
                        "payments_ready": payments_ready()})


@app.post("/api/documents")
async def api_upload(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    if not gemini_ready():
        return err_response(503, "The AI engine is being configured. Please try again shortly.")
    ip = request.client.host if request.client else "unknown"
    if not rate_ok(ip):
        return err_response(429, "Too many requests. Please wait a while and try again.")
    limited = daily_limit_response(request, "ai", "AI runs")
    if limited:
        return limited
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
    limited = daily_limit_response(request, "ai", "AI runs")
    if limited:
        return None, limited
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
    db_history(doc_id, "summary", output_preview=out)
    db_usage("ai_call", {"action": "summary"})
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
    db_history(doc_id, "analyze", output_preview=out)
    db_usage("ai_call", {"action": "analyze"})
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
    db_history(doc_id, "extract", output_preview=json.dumps(fields)[:2000])
    db_usage("ai_call", {"action": "extract"})
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
    db_history(doc_id, "chat", input_preview=question, output_preview=out)
    db_insert_async("conversations", {"doc_id": doc_id, "role": "user", "message": question[:2000]})
    db_insert_async("conversations", {"doc_id": doc_id, "role": "assistant", "message": out[:4000]})
    db_usage("ai_call", {"action": "chat"})
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
    limited = daily_limit_response(request, "doc", "documents")
    if limited:
        return limited
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
    db_history(doc_id if doc_id else None, "career:" + slug,
               input_preview=json.dumps(fields)[:500], output_preview=out)
    db_usage("career:" + slug)
    return JSONResponse({"result": out})


@app.post("/api/hr/document/{slug}")
async def api_hr_document(slug: str, request: Request):
    spec = HR_DOCS.get(slug)
    if not spec:
        return err_response(404, "Unknown document.")
    limited = daily_limit_response(request, "doc", "documents")
    if limited:
        return limited
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
