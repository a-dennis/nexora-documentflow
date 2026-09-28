from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Nexora", version="1.0.0")

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexora — AI Work Tools</title>
<style>
:root{--bg:#f7f9fc;--surface:#fff;--ink:#182033;--muted:#667085;--line:#e6eaf0;--blue:#2563eb;--blue-dark:#1d4ed8;--blue-soft:#eff6ff;--shadow:0 18px 50px rgba(15,23,42,.08)}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:radial-gradient(circle at 10% 0%,rgba(219,234,254,.8),transparent 30%),radial-gradient(circle at 90% 10%,rgba(224,231,255,.7),transparent 28%),var(--bg)}
header{height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 6%;background:rgba(255,255,255,.88);border-bottom:1px solid rgba(230,234,240,.8);backdrop-filter:blur(14px);position:sticky;top:0;z-index:10}
.brand{display:flex;align-items:center;gap:11px;font-weight:800;font-size:20px}.logo{width:36px;height:36px;border-radius:11px;display:grid;place-items:center;color:#fff;font-weight:900;background:linear-gradient(135deg,#2563eb,#4f46e5);box-shadow:0 8px 18px rgba(37,99,235,.22)}
.nav{display:flex;gap:8px}.nav button{border:0;background:transparent;padding:10px 14px;border-radius:10px;color:#475467;font-weight:650;cursor:pointer}.nav button:hover{background:#f2f4f7;color:#182033}
main{max-width:1180px;margin:0 auto;padding:58px 24px 70px}.hero{text-align:center;max-width:850px;margin:0 auto 38px}.eyebrow{display:inline-flex;padding:7px 12px;border-radius:999px;background:var(--blue-soft);color:var(--blue-dark);font-size:13px;font-weight:750;border:1px solid #dbeafe}
h1{font-size:clamp(38px,6vw,64px);line-height:1.03;margin:18px 0 14px;letter-spacing:-2px}.hero p{font-size:18px;line-height:1.65;color:var(--muted);margin:0}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.card{background:rgba(255,255,255,.95);border:1px solid var(--line);border-radius:22px;padding:28px;box-shadow:var(--shadow);transition:.18s ease}.card:hover{transform:translateY(-3px);box-shadow:0 24px 60px rgba(15,23,42,.11)}
.icon{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:var(--blue-soft);font-size:23px;margin-bottom:18px}.card h2{margin:0 0 8px;font-size:22px}.card p{color:var(--muted);line-height:1.6;margin:0 0 20px}.actions{display:flex;flex-wrap:wrap;gap:10px}
.btn{border:1px solid #bfdbfe;background:var(--blue-soft);color:var(--blue-dark);padding:11px 16px;border-radius:11px;font-weight:750;cursor:pointer}.btn.primary{background:var(--blue);border-color:var(--blue);color:#fff}.btn.primary:hover{background:var(--blue-dark)}
.section{margin-top:28px}.section-title{font-size:15px;font-weight:800;color:#475467;margin:0 0 12px}.footer{text-align:center;color:#98a2b3;font-size:13px;margin-top:44px}
@media(max-width:720px){header{padding:0 16px}.nav button{padding:9px 8px}main{padding:38px 16px}.grid{grid-template-columns:1fr}h1{letter-spacing:-1px}}
</style>
</head>
<body>
<header><div class="brand"><div class="logo">N</div><span>Nexora</span></div><nav class="nav"><button onclick="topPage()">Home</button><button onclick="coming('Document AI')">Document AI</button><button onclick="coming('HR & Career')">HR & Career</button></nav></header>
<main>
<section class="hero"><span class="eyebrow">NEXORA AI WORKSPACE</span><h1>AI tools that get work done.</h1><p>Document intelligence and practical HR & career tools in one focused workspace.</p></section>
<section class="grid">
<article class="card"><div class="icon">📄</div><h2>Document AI Intelligence</h2><p>Summarize documents, ask questions, extract structured data and turn documents into useful outputs.</p><div class="actions"><button class="btn primary" onclick="coming('Document AI')">Open Document AI</button></div></article>
<article class="card"><div class="icon">💼</div><h2>HR & Career Intelligence</h2><p>Practical AI tools for resumes, job descriptions, offer letters and everyday HR work.</p><div class="actions"><button class="btn primary" onclick="coming('HR & Career')">Open HR & Career</button></div></article>
</section>
<section class="section"><p class="section-title">Featured Career Tools</p><div class="grid">
<article class="card"><div class="icon">📄</div><h2>Resume Builder & ATS Optimizer</h2><p>Prepare a stronger, job-focused resume from your existing information.</p><div class="actions"><button class="btn" onclick="coming('Resume Builder')">Open</button></div></article>
<article class="card"><div class="icon">🎯</div><h2>JD Builder & Recruitment Optimizer</h2><p>Create clearer, structured job descriptions designed for practical recruitment workflows.</p><div class="actions"><button class="btn" onclick="coming('JD Builder')">Open</button></div></article>
</div></section>
<div class="footer">Nexora — development version</div>
</main>
<script>
function coming(name){alert(name+" is the next module we will connect here.");}
function topPage(){window.scrollTo({top:0,behavior:"smooth"});}
</script>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/health")
def health():
    return {"status": "ok", "service": "nexora"}
