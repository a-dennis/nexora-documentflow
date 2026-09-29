"""
Nexora - Phase 1 production shell.

A small FastAPI website that renders the Nexora landing page and
placeholder sections, ready to deploy on Render.

Routes:
  /                Home
  /document-ai     Document AI section (placeholder)
  /hr-career       HR & Career section (placeholder)
  /resume-builder  Resume Builder + ATS Optimizer (featured placeholder)
  /jd-builder      JD Builder + Recruitment Optimizer (featured placeholder)
  /health          JSON health check for Render
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Nexora", docs_url=None, redoc_url=None, openapi_url=None)

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

/* ---------- buttons ---------- */
.btn {
  display: inline-block; min-height: 46px; padding: 12px 20px;
  font-size: 15px; font-weight: 600; border-radius: 10px;
  background: var(--accent); color: #ffffff; border: 1px solid var(--accent);
}
.btn:hover { background: var(--accent-dark); text-decoration: none; }
.btn.ghost { background: #ffffff; color: var(--accent); border: 1px solid #c4d4f5; }
.btn.ghost:hover { background: var(--tint); }
.btn.disabled, .btn.disabled:hover {
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
                 "Open Document AI")}
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
    {card("doc", "Document Summarizer", "Turn long documents into short, clear summaries.", badge="Soon")}
    {card("chat", "Document Q&amp;A", "Ask questions and get answers straight from your files.", badge="Soon")}
    {card("table", "Data Extraction", "Pull key fields and tables out of documents into Excel.", badge="Soon")}
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


def document_ai_page() -> str:
    tools = [
        ("doc", "Summarize Documents", "Short, accurate summaries of long PDFs, Word files and reports."),
        ("chat", "Ask Questions About Documents", "Chat with your document and get answers with the relevant parts pointed out."),
        ("table", "Extract Data", "Pull names, amounts, dates and tables out of documents into Excel."),
        ("search", "Analyze Documents", "Deep analysis: risks, key points, comparisons and missing information."),
        ("pdf", "PDF &amp; Document Tools", "Practical PDF and document utilities for daily office work."),
        ("folder", "Document Workspace", "Keep your uploaded documents, chats and results organized in one place."),
    ]
    cards = "".join(card(i, t, d, badge="Soon") for i, t, d in tools)
    body = f"""
<section class="page-hero"><div class="container">
  <h1>Document AI Intelligence</h1>
  <p>Upload a document and let AI summarize it, answer your questions and
  extract the data you need.</p>
</div></section>
<section class="section"><div class="container">
  <div class="grid three">{cards}</div>
  <div class="note">These tools are being moved from the working Nexora
  prototype to this new platform. They will switch on here one by one -
  starting with document upload and summaries.</div>
</div></section>
"""
    return page("Document AI", "Document AI: summarize, question, extract and analyze your documents with AI.", "/document-ai", body)


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
# Routes
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
