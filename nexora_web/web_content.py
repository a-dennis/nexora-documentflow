"""HTML, CSS and content constants for Nexora (split from app.py)."""

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

/* ============ Nexora design refresh (Sep 2026) ============ */
:root {
  --bg: #eef2ff;
  --accent: #4f46e5;
  --accent-dark: #4338ca;
  --accent2: #7c3aed;
  --tint: #eef0ff;
  --radius: 18px;
}
body {
  background:
    radial-gradient(900px 480px at 85% -80px, #e0e7ff 0%, rgba(224,231,255,0) 60%),
    radial-gradient(700px 420px at -10% 120px, #f3e8ff 0%, rgba(243,232,255,0) 55%),
    linear-gradient(180deg, #f6f7ff 0%, #eef2f9 100%);
  background-attachment: fixed;
}
.topnav {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 1px 0 rgba(15, 23, 42, 0.05), 0 8px 24px rgba(79, 70, 229, 0.06);
}
.brand span {
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.navlinks a { border-radius: 999px; padding: 8px 14px; }
.navlinks a.active {
  color: #ffffff;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
}
.hero h1, .page-hero h1 { letter-spacing: -0.8px; }
.kicker { color: var(--accent2); }

/* cards */
.card {
  border-radius: var(--radius);
  border: 1px solid rgba(99, 102, 241, 0.14);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.card-link:hover, a.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgba(79, 70, 229, 0.16);
  text-decoration: none;
  border-color: rgba(99, 102, 241, 0.35);
}
.card-icon {
  width: 46px; height: 46px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 23px; line-height: 1;
  background: linear-gradient(135deg, #eef0ff 0%, #f5edff 100%);
  border: 1px solid rgba(99, 102, 241, 0.18);
  color: inherit;
}
.card-icon svg { display: none; }

/* buttons: pill shape, gradient, clear press feedback */
.btn {
  border-radius: 999px;
  padding: 12px 24px;
  font-weight: 700;
  letter-spacing: 0.1px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.32);
  border: none;
  transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
}
.btn:hover {
  background: linear-gradient(135deg, var(--accent-dark) 0%, #6d28d9 100%);
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(79, 70, 229, 0.4);
}
.btn:active { transform: translateY(0); box-shadow: 0 3px 8px rgba(79, 70, 229, 0.3); }
.btn.ghost {
  background: #ffffff;
  color: var(--accent);
  border: 1.5px solid #c7d0fb;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
}
.btn.ghost:hover { background: var(--tint); color: var(--accent-dark); transform: translateY(-1px); }

/* tags / badges */
.tag {
  border-radius: 999px; font-weight: 700; letter-spacing: 0.4px;
}
.tag.live {
  background: linear-gradient(135deg, #dcfce7, #d1fae5); color: #047857;
  border: 1px solid #a7f3d0;
}
.tag.featured {
  background: linear-gradient(135deg, #ede9fe, #e0e7ff); color: var(--accent-dark);
  border: 1px solid #c7d2fe;
}
.tag.soon { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

/* inputs */
.field input, .field textarea, .field select,
.chatrow input {
  border-radius: 12px;
  border: 1.5px solid #dbe1f0;
  background: #fbfcff;
}
.field input:focus, .field textarea:focus, .field select:focus,
.chatrow input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

/* pill tabs */
.pill-tabs button { border-radius: 999px; border: 1.5px solid #dbe1f0; }
.pill-tabs button.active {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* hero polish */
.page-hero, .hero { padding-top: 56px; }
.dropzone, .srcbox { border-radius: var(--radius); }

@media (max-width: 760px) {
  .hero, .page-hero { padding-top: 40px; }
  .btn { padding: 13px 22px; font-size: 15px; }
}

/* ilovepdf-style tools grid */
.cat-pills{display:flex;flex-wrap:wrap;gap:10px;margin:2px 0 26px}
.cat-pills button{border:1px solid var(--line);background:#fff;border-radius:999px;padding:9px 18px;font:inherit;font-size:14px;font-weight:600;cursor:pointer;color:var(--ink);transition:all .15s}
.cat-pills button:hover{border-color:var(--accent);color:var(--accent)}
.cat-pills button.active{background:#161322;border-color:#161322;color:#fff}
.tools-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
a.tool-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px 20px;display:block;text-decoration:none;color:inherit;transition:transform .18s ease,box-shadow .18s ease,border-color .18s}
a.tool-card:hover{transform:translateY(-4px);box-shadow:0 14px 30px rgba(76,60,229,.13);border-color:rgba(76,60,229,.25)}
a.tool-card .t-icon{font-size:32px;line-height:1;margin-bottom:14px}
a.tool-card h3{margin:0 0 6px;font-size:16.5px}
a.tool-card p{margin:0;color:var(--muted);font-size:13.5px;line-height:1.55}
a.tool-card.hide{display:none}
@media(max-width:1024px){.tools-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:760px){.tools-grid{grid-template-columns:repeat(2,1fr);gap:12px}a.tool-card{padding:18px 16px}a.tool-card .t-icon{font-size:26px;margin-bottom:10px}a.tool-card h3{font-size:15px}}

/* ============ Nexora signature accent refresh (Sep 2026, round 2) ============ */
/* Bold violet-to-fuchsia signature: ilovepdf energy, Nexora's own color. */
:root {
  --accent: #7c3aed;
  --accent-dark: #6d28d9;
  --accent2: #db2777;
  --tint: #f6f1ff;
  --bg: #fbfaff;
}
body {
  background:
    radial-gradient(1000px 540px at 88% -120px, rgba(219, 39, 119, 0.13) 0%, rgba(219, 39, 119, 0) 60%),
    radial-gradient(840px 480px at -12% 40px, rgba(124, 58, 237, 0.15) 0%, rgba(124, 58, 237, 0) 55%),
    radial-gradient(760px 520px at 50% 118%, rgba(99, 102, 241, 0.10) 0%, rgba(99, 102, 241, 0) 62%),
    linear-gradient(180deg, #fdfbff 0%, #f9f7ff 55%, #f6f8fc 100%);
  background-attachment: fixed;
}
.kicker { color: var(--accent2); }
.brand span {
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.navlinks a.active {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  box-shadow: 0 4px 14px rgba(168, 60, 200, 0.38);
}

/* buttons: bold gradient, real depth, lively hover */
.btn {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
  box-shadow: 0 8px 20px rgba(168, 60, 200, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.btn:hover {
  background: linear-gradient(135deg, #8b5cf6 0%, #e0358a 100%);
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(168, 60, 200, 0.44),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 10px rgba(168, 60, 200, 0.34);
}
.btn.ghost {
  background: #ffffff; color: var(--accent);
  border: 1.5px solid #d9c8fb;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);
}
.btn.ghost:hover {
  background: var(--tint); color: var(--accent-dark);
  border-color: var(--accent); transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(124, 58, 237, 0.16);
}

/* cards: icon chips, richer hover */
.card-icon {
  background: linear-gradient(135deg, #f3ecff 0%, #ffe9f4 100%);
  border: 1px solid rgba(124, 58, 237, 0.16);
}
a.card-link:hover, a.card:hover {
  box-shadow: 0 16px 34px rgba(124, 58, 237, 0.18);
  border-color: rgba(124, 58, 237, 0.4);
}
a.tool-card { border: 1px solid rgba(15, 23, 42, 0.07); box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04); }
a.tool-card .t-icon {
  width: 56px; height: 56px; border-radius: 16px; font-size: 28px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #f3ecff 0%, #ffe9f4 100%);
  border: 1px solid rgba(124, 58, 237, 0.14);
  transition: transform .18s ease, box-shadow .18s ease;
}
a.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 34px rgba(124, 58, 237, 0.17);
  border-color: rgba(124, 58, 237, 0.38);
}
a.tool-card:hover .t-icon {
  transform: scale(1.06);
  box-shadow: 0 6px 16px rgba(219, 39, 119, 0.22);
  border-color: rgba(219, 39, 119, 0.3);
}
a.tool-card h3 { letter-spacing: -0.2px; }

/* category pills: confident dark active like the reference, accent hover */
.cat-pills button:hover { border-color: var(--accent); color: var(--accent); box-shadow: 0 3px 10px rgba(124, 58, 237, 0.12); }
.cat-pills button.active { background: #1b1430; border-color: #1b1430; color: #fff; box-shadow: 0 4px 12px rgba(27, 20, 48, 0.3); }

/* accents elsewhere */
.pill-tabs button.active {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  box-shadow: 0 4px 12px rgba(168, 60, 200, 0.32);
}
.msg.user { background: linear-gradient(135deg, var(--accent), var(--accent2)); }
.tabs button.active { color: var(--accent); border-bottom-color: var(--accent); }
.sugg button:hover { background: var(--tint); border-color: var(--accent); }
.dropzone:hover, .dropzone.drag { border-color: var(--accent); background: var(--tint); }
.field input:focus, .field textarea:focus, .field select:focus,
.chatrow input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.16);
}
.tag.featured {
  background: linear-gradient(135deg, #f3ecff, #ffe9f4);
  color: var(--accent-dark); border: 1px solid #ddc9fb;
}
table.kv th { background: var(--tint); }
.spin { border-top-color: var(--accent); }
@media(max-width:760px){a.tool-card .t-icon{width:48px;height:48px;font-size:24px;border-radius:14px}}
/* ---------- post-task success panel & share ---------- */
.success-panel { text-align: center; }
.success-check {
  width: 62px; height: 62px; margin: 0 auto 12px; border-radius: 50%;
  background: linear-gradient(135deg, #22c55e, #10b981); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 30px; font-weight: 800;
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.35);
}
.success-panel h3 { margin: 0 0 6px; font-size: 22px; letter-spacing: -0.3px; }
.success-panel .success-msg { margin: 0 0 14px; color: var(--muted); font-size: 15px; }
.success-panel .btn-download {
  width: 100%; font-size: 17px; min-height: 52px;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
}
.success-next { margin-top: 22px; text-align: left; }
.success-next h4, .success-share h4 {
  margin: 0 0 10px; font-size: 13px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 1.1px; color: var(--muted);
}
.next-tools { display: flex; flex-wrap: wrap; gap: 8px; }
.next-tools a {
  display: inline-block; padding: 9px 14px; border-radius: 999px;
  background: var(--tint); color: var(--accent-dark);
  font-weight: 600; font-size: 14px;
  border: 1px solid rgba(124, 58, 237, 0.18);
}
.next-tools a:hover {
  text-decoration: none; color: #fff;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
}
.success-share { margin-top: 20px; text-align: left; }
.share-row { display: flex; flex-wrap: wrap; gap: 8px; }
.share-btn {
  display: inline-flex; align-items: center; gap: 7px; padding: 9px 14px;
  border-radius: 999px; font-weight: 600; font-size: 14px; cursor: pointer;
  border: 1px solid var(--line); background: #fff; color: var(--ink);
}
.share-btn:hover {
  text-decoration: none; transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.10);
}
.share-btn .dot { width: 10px; height: 10px; border-radius: 50%; }
.share-btn.wa .dot { background: #25d366; }
.share-btn.tg .dot { background: #229ed9; }
.share-btn.x .dot { background: #111111; }
.share-btn.li .dot { background: #0a66c2; }
.share-btn.copy .dot { background: #7c3aed; }
.share-btn.copy.copied { background: var(--green-tint); color: var(--green); border-color: #b7e4c9; }
.share-note { margin: 10px 0 0; font-size: 13px; color: var(--muted); }

"""

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

SUCCESS_JS = r"""
<script>
(function () {
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  window.nexoraSuccess = function (mount, opts) {
    opts = opts || {};
    var box = (typeof mount === 'string') ? document.getElementById(mount) : mount;
    if (!box) { return; }
    var pageUrl = location.origin + (opts.path || location.pathname);
    var shareText = (opts.shareText || 'I just used Nexora - free, no sign-up. Try it: ') + pageUrl;
    var h = '<div class="success-check">&#10003;</div>';
    h += '<h3>' + esc(opts.heading || 'Done!') + '</h3>';
    if (opts.message) { h += '<p class="success-msg">' + esc(opts.message) + '</p>'; }
    if (opts.download) {
      h += '<a class="btn btn-download" href="' + opts.download.url
        + '" download="' + esc(opts.download.name || 'download') + '">&#11015; Download '
        + esc(opts.download.label || opts.download.name || 'file') + '</a>';
    }
    if (opts.next && opts.next.length) {
      h += '<div class="success-next"><h4>Continue to...</h4><div class="next-tools">';
      opts.next.forEach(function (n) {
        h += '<a href="' + esc(n[0]) + '">' + esc(n[1]) + '</a>';
      });
      h += '</div></div>';
    }
    h += '<div class="success-share"><h4>Spread the word - it keeps Nexora free</h4><div class="share-row">';
    h += '<a class="share-btn wa" target="_blank" rel="noopener" href="https://wa.me/?text='
      + encodeURIComponent(shareText) + '"><span class="dot"></span>WhatsApp</a>';
    h += '<a class="share-btn tg" target="_blank" rel="noopener" href="https://t.me/share/url?url='
      + encodeURIComponent(pageUrl) + '&text='
      + encodeURIComponent(opts.shareText || 'I just used Nexora - free, no sign-up. Try it: ')
      + '"><span class="dot"></span>Telegram</a>';
    h += '<a class="share-btn x" target="_blank" rel="noopener" href="https://twitter.com/intent/tweet?text='
      + encodeURIComponent(shareText) + '"><span class="dot"></span>X</a>';
    h += '<a class="share-btn li" target="_blank" rel="noopener" href="https://www.linkedin.com/sharing/share-offsite/?url='
      + encodeURIComponent(pageUrl) + '"><span class="dot"></span>LinkedIn</a>';
    h += '<button class="share-btn copy" type="button"><span class="dot"></span><span class="copy-label">Copy link</span></button>';
    h += '</div><p class="share-note">Loving Nexora? Send it to one friend - that helps us more than any ad.</p></div>';
    box.innerHTML = h;
    var copyBtn = box.querySelector('.share-btn.copy');
    copyBtn.addEventListener('click', function () {
      var done = function () {
        copyBtn.classList.add('copied');
        copyBtn.querySelector('.copy-label').textContent = 'Copied!';
        setTimeout(function () {
          copyBtn.classList.remove('copied');
          copyBtn.querySelector('.copy-label').textContent = 'Copy link';
        }, 2000);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareText).then(done, done);
      } else {
        var ta = document.createElement('textarea');
        ta.value = shareText;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (e) {}
        ta.remove();
        done();
      }
    });
    box.style.display = 'block';
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };
})();
</script>
"""


EMOJI = {
    "doc": "\U0001F4C4", "briefcase": "\U0001F4BC", "resume": "\U0001F4DD",
    "target": "\U0001F3AF", "search": "\U0001F50D", "calc": "\U0001F9EE",
    "pen": "\u270D\uFE0F", "chat": "\U0001F4AC", "table": "\U0001F4CA",
    "pdf": "\U0001F4D5", "letter": "\u2709\uFE0F", "check": "\u2705",
    "folder": "\U0001F4C1", "upload": "\u2B06\uFE0F",
    "money": "\U0001F4B0", "chart": "\U0001F4C8", "gift": "\U0001F381",
    "calendar": "\U0001F4C5", "megaphone": "\U0001F4E3", "mag": "\U0001F9D0",
    "page": "\U0001F4D1",
    "merge": "\U0001F517", "split": "\u2702\uFE0F", "compress": "\U0001F5DC\uFE0F",
    "word": "\U0001F4DD", "ppt": "\U0001F4FD", "excel": "\U0001F4CA",
    "image": "\U0001F5BC\uFE0F", "sign": "\u2712\uFE0F", "stamp": "\U0001F516",
    "rotate": "\U0001F504", "code": "\U0001F310", "unlock": "\U0001F513",
    "lock": "\U0001F512", "organize": "\U0001F5C2\uFE0F", "wrench": "\U0001F527",
    "numbers": "\U0001F522", "scan": "\U0001F4F7", "ocr": "\U0001F441\uFE0F",
    "compare": "\u2696\uFE0F", "redact": "\u2B1B", "crop": "\U0001F532",
    "markdown": "\U0001F4D8", "txt": "\U0001F4C3", "images": "\U0001F5BE",
    "gray": "\U0001F311",
}

DOCUMENT_AI_BODY = r"""
<section class="page-hero"><div class="container">
  <span class="tag live">Document AI</span>
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

  <div class="success-panel card" id="shareStrip" style="display:none;margin-top:16px"></div>

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
    var strip = document.getElementById('shareStrip');
    if (strip) { strip.style.display = 'none'; strip.innerHTML = ''; }
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

  function showShare(action) {
    window.nexoraSuccess('shareStrip', {
      heading: 'Done! ' + action + ' complete',
      message: 'Nexora AI just worked through your document in seconds.',
      next: [['/career/resume-builder', 'Resume Builder'],
             ['/career/ats-optimizer', 'ATS Optimizer'],
             ['/pdf/merge', 'Merge PDF'],
             ['/pdf/compress', 'Compress PDF']],
      shareText: 'I just used Nexora Document AI on a file - free, no sign-up. Try it: ',
      path: '/document-ai'
    });
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
        showShare('Summary');
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
        showShare('Data extraction');
      });
  });

  document.getElementById('runAnalyze').addEventListener('click', function () {
    var btn = this;
    aiCall('/api/documents/' + docId + '/analyze', {}, btn,
      document.getElementById('errAnalyze'), function (j) {
        renderMarkdownLite(document.getElementById('outAnalyze'), j.analysis);
        showShare('Analysis');
      });
  });
})();
</script>
""" + SUCCESS_JS

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
  <span class="tag live">HR &amp; Career</span>
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
    <div class="success-panel" id="successBox" style="display:none;margin-top:18px;border-top:1px solid var(--line);padding-top:18px"></div>
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
      window.nexoraSuccess("successBox", {
        heading: "Done! Your result is ready",
        message: CFG.title + " finished. Review it above, then send Nexora to a friend.",
        next: CFG.next || [],
        shareText: "I just used Nexora " + CFG.title + " - free AI, no sign-up. Try it: ",
        path: "/career/" + CFG.slug
      });
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
""" + SUCCESS_JS

CALC_BODY = """
<section class="page-hero"><div class="container">
  <span class="tag live">Calculators</span>
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
  {id: "ctc", name: "🧮 CTC Breakdown",
   desc: "See how an annual CTC typically splits into components.",
   fields: [["ctc", "Annual CTC (Rs.)", "e.g. 600000"]],
   note: "A common structure: Basic 40% of CTC, HRA 50% of Basic, employer PF 12% of Basic, gratuity 4.81% of Basic, rest as special allowance. Actual structures vary by company."},
  {id: "takehome", name: "💰 Take-home Pay",
   desc: "Estimate monthly in-hand salary from CTC (new tax regime).",
   fields: [["ctc", "Annual CTC (Rs.)", "e.g. 600000"]],
   note: "Simplified estimate using the new regime (FY 2025-26) with Rs. 75,000 standard deduction, employee PF 12% of Basic (40% of CTC) and Rs. 200/month professional tax. Actual take-home depends on your company's structure and your tax choices."},
  {id: "increment", name: "📈 Increment",
   desc: "New salary after a percentage hike.",
   fields: [["cur", "Current annual CTC (Rs.)", "e.g. 600000"], ["pct", "Hike (%)", "e.g. 12"]],
   note: ""},
  {id: "gratuity", name: "🎁 Gratuity",
   desc: "Gratuity payable under the Payment of Gratuity Act.",
   fields: [["basic", "Last drawn monthly Basic + DA (Rs.)", "e.g. 25000"], ["years", "Years of service", "e.g. 6"]],
   note: "Formula: 15/26 x last drawn Basic+DA x completed years (6+ months rounds up). Gratuity generally applies after 5 years of continuous service."},
  {id: "notice", name: "📅 Notice Period",
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

SEO_CALC_PAGES = {
    "ctc-calculator": {
        "calc": "ctc",
        "title": "CTC Breakdown Calculator",
        "meta": "Free CTC breakdown calculator for India. See how your annual CTC splits into Basic, HRA, PF, gratuity and allowances - yearly and monthly.",
        "h1": "CTC Breakdown Calculator",
        "intro": "CTC (Cost to Company) is the total your employer spends on you in a year, but it is not what lands in your bank account. Enter your annual CTC to see a typical split into Basic salary, HRA, employer PF, gratuity and special allowance.",
        "how": ["Enter your annual CTC in rupees (the number in your offer letter).",
                "The calculator applies a common Indian salary structure: Basic 40% of CTC, HRA 50% of Basic, employer PF 12% of Basic, gratuity 4.81% of Basic.",
                "Read your yearly and monthly Basic, and each component, instantly."],
        "example": "Example: on a Rs. 6,00,000 CTC, Basic is typically Rs. 2,40,000/year (Rs. 20,000/month), HRA Rs. 1,20,000, employer PF Rs. 28,800 and gratuity about Rs. 11,544.",
        "faqs": [["Is CTC the same as take-home salary?", "No. CTC includes components you never receive in cash, like employer PF and gratuity. Take-home is CTC minus PF, professional tax and income tax. Use our take-home salary calculator for that estimate."],
                 ["Does every company use this exact structure?", "No. Structures vary - some companies keep Basic at 50% of CTC, some cap PF at Rs. 1,800/month. Treat this as a typical structure and check your salary slip for your actual split."],
                 ["Is my salary data stored anywhere?", "No. This calculator runs entirely in your browser. Nothing you enter is sent to our servers."]],
    },
    "salary-calculator": {
        "calc": "takehome",
        "title": "Take-home Salary Calculator",
        "meta": "Free take-home salary calculator for India (new tax regime). Estimate your monthly in-hand salary from CTC after PF, professional tax and income tax.",
        "h1": "Take-home Salary Calculator (In-hand)",
        "intro": "Your offer letter says CTC, but what matters every month is the in-hand amount. Enter your annual CTC to estimate your monthly take-home salary under the new tax regime, after employee PF, professional tax and income tax.",
        "how": ["Enter your annual CTC in rupees.",
                "The calculator estimates employee PF (12% of Basic at 40% of CTC), Rs. 200/month professional tax, and income tax under the new regime (FY 2025-26) with the Rs. 75,000 standard deduction.",
                "See your estimated monthly take-home and each deduction."],
        "example": "Example: a Rs. 6,00,000 CTC typically works out to roughly Rs. 45,000-47,000 per month in hand, depending on your company's PF and structure.",
        "faqs": [["Which tax regime does this use?", "The new regime for FY 2025-26, where income up to Rs. 12 lakh (taxable) effectively pays zero tax after the rebate. The old regime needs your investment details, so it is not estimated here."],
                 ["Why is my actual in-hand different?", "Companies structure salaries differently - PF caps, variable pay, gratuity in CTC and reimbursements all move the number. Use this as a close estimate, then verify with your offer breakup."],
                 ["Is my salary data stored anywhere?", "No. Everything runs in your browser and nothing is sent to our servers."]],
    },
    "increment-calculator": {
        "calc": "increment",
        "title": "Salary Increment Calculator",
        "meta": "Free salary increment calculator. Enter your current CTC and hike percentage to see your new salary, plus the increase per year and per month.",
        "h1": "Salary Increment Calculator",
        "intro": "Got a hike percentage and want the real numbers? Enter your current annual CTC and the hike percent to see your new CTC and how much more you earn per year and per month.",
        "how": ["Enter your current annual CTC.",
                "Enter the hike percentage (for example 12 for a 12% hike).",
                "See your new CTC, the yearly increase and the monthly increase."],
        "example": "Example: a 12% hike on a Rs. 6,00,000 CTC gives a new CTC of Rs. 6,72,000 - that is Rs. 72,000 more per year, or Rs. 6,000 more per month.",
        "faqs": [["Is the hike always on the full CTC?", "Usually yes for appraisals, but some companies apply the percentage only to Basic. Check your increment letter - if it is on Basic, enter your Basic here instead."],
                 ["How do I compare two job offers?", "Run both CTCs through the take-home salary calculator - a higher CTC does not always mean higher in-hand if the structure differs."]],
    },
    "gratuity-calculator": {
        "calc": "gratuity",
        "title": "Gratuity Calculator",
        "meta": "Free gratuity calculator for India. Calculate gratuity payable under the Payment of Gratuity Act from your last drawn Basic + DA and years of service.",
        "h1": "Gratuity Calculator (India)",
        "intro": "Gratuity is a lump sum your employer pays when you leave after long service. Under the Payment of Gratuity Act, it is 15/26 of your last drawn Basic + DA for each completed year. Enter your details to see the amount payable.",
        "how": ["Enter your last drawn monthly Basic + DA (not full CTC).",
                "Enter your years of service - 6 months or more rounds up to a full year.",
                "See the gratuity payable under the standard formula."],
        "example": "Example: with Rs. 25,000 Basic + DA and 6 years of service, gratuity is 15/26 x 25,000 x 6, about Rs. 86,538.",
        "faqs": [["When am I eligible for gratuity?", "Generally after 5 years of continuous service with the same employer. The 5-year rule does not apply in cases of death or disablement."],
                 ["Is gratuity taxable?", "For most private-sector employees, gratuity up to Rs. 20 lakh is tax-exempt. Amounts above that are taxed as income."],
                 ["My company is not covered by the Act - what changes?", "The formula becomes 15/30 (half month) instead of 15/26 per year. Most registered companies with 10+ employees are covered by the Act."]],
    },
    "notice-period-calculator": {
        "calc": "notice",
        "title": "Notice Period Calculator",
        "meta": "Free notice period calculator. Enter your resignation date and notice days to find your last working day instantly.",
        "h1": "Notice Period Calculator - Last Working Day",
        "intro": "Resigning and need to know your last working day? Enter your resignation date and the notice period in your appointment letter to see the exact date you finish.",
        "how": ["Pick your resignation date (the day you submit your resignation).",
                "Enter your notice period in days - 30, 60 or 90 are common in India.",
                "See your last working day, counting calendar days."],
        "example": "Example: resigning on 1 October with a 30-day notice period makes your last working day 31 October.",
        "faqs": [["Does the notice period count weekends and holidays?", "This calculator counts calendar days, which is the common practice. Some companies count only working days - check your appointment letter."],
                 ["Can I leave earlier than my notice period?", "Often yes, with a notice buy-out (paying salary in lieu) or by adjusting earned leave. Both need your employer's agreement."]],
    },
}

SEO_CAREER_PAGES = {
    "resume-ats-checker": {
        "career": "ats-optimizer",
        "title": "Resume ATS Checker - Free ATS Score",
        "meta": "Free resume ATS checker. Paste your resume and the job description to get your ATS match score, missing keywords and concrete fixes.",
        "h1": "Resume ATS Checker",
        "intro": "Most companies screen resumes with an ATS (applicant tracking system) before a human reads them. Paste your resume and the job description below to see your match score, the keywords you are missing, and exactly what to fix.",
        "faqs": [["What is an ATS?", "Applicant tracking systems are software companies use to collect, scan and rank resumes. They look for keywords, skills and titles that match the job description - resumes that match poorly often never reach a recruiter."],
                 ["What ATS score should I aim for?", "There is no universal pass mark, but matching most of the job's core skills and keywords (roughly 70-80%+) puts you in a strong position. Use the missing-keyword list to close the gaps honestly."],
                 ["Should I add keywords I do not have experience in?", "No. Only add skills you can back up in an interview. The goal is to surface your real experience in the language the job description uses, not to game the screen."],
                 ["Is my resume stored?", "Your text is sent to the AI model to produce the analysis and is not shown to anyone else. Avoid pasting phone numbers or addresses if you prefer."]],
    },
    "offer-letter-analyzer": {
        "career": "offer-letter-analyzer",
        "title": "Offer Letter Analyzer - Free AI Review",
        "meta": "Free offer letter analyzer for India. Paste your offer letter to get the CTC structure, red flags, missing clauses and negotiation points explained in plain language.",
        "h1": "Offer Letter Analyzer",
        "intro": "Offer letters hide a lot inside the CTC number. Paste yours below (remove personal details if you like) and get a plain-language breakdown: what the CTC really includes, red flags to watch, clauses that are missing, and points worth negotiating.",
        "faqs": [["What should I check first in an offer letter?", "Start with the CTC breakup (how much is fixed vs variable), the notice period, and any bond or service agreement. Those three affect your money and your freedom to move more than anything else."],
                 ["Is a higher CTC always better?", "Not always. A higher CTC with a large variable component, a long notice period, or a bond can be worse than a lower, cleaner offer. Compare the estimated in-hand with our take-home salary calculator."],
                 ["Can this replace a lawyer's review?", "No. This is an AI reading aid that highlights what to look at - for a bond, non-compete or anything you are unsure about, get proper legal advice."]],
    },
    "cover-letter-generator": {
        "career": "cover-letter-builder",
        "title": "Cover Letter Generator - Free AI Writer",
        "meta": "Free AI cover letter generator. Answer a few questions about the role and your experience and get a professional, ready-to-edit cover letter in seconds.",
        "h1": "Cover Letter Generator",
        "intro": "A good cover letter connects your experience to the specific job, and most people stare at a blank page instead. Answer a few short questions about the role and your background and get a professional draft you can edit and send.",
        "faqs": [["Do recruiters actually read cover letters?", "Many do, especially for competitive roles and smaller companies. A short, specific letter that mirrors the job's language can tip a borderline application. A generic one does nothing."],
                 ["How long should a cover letter be?", "Three to four short paragraphs - under a page. Lead with why this role, prove it with one or two concrete achievements, and close with a clear next step."],
                 ["Should I send the AI draft as-is?", "Edit it first. Add one specific detail only you could write - a project name, a number, a reason you want this company. That is what makes it read like you."]],
    },
    "jd-quality-checker": {
        "career": "jd-analyzer",
        "title": "JD Quality Checker - Free Job Description Analyzer",
        "meta": "Free job description quality checker. Paste your JD to find vague language, missing sections, biased wording and fixes that attract better candidates.",
        "h1": "JD Quality Checker",
        "intro": "A weak job description gets weak applicants. Paste your JD below to see what is vague, what is missing (salary range, location, must-haves vs nice-to-haves), wording that quietly filters out good candidates, and how to fix it.",
        "faqs": [["What makes a job description good?", "Clear title, specific responsibilities, a short must-have list separated from nice-to-haves, salary range and location, and a human tone. Vague superlatives and 15-item requirement lists drive away strong candidates."],
                 ["Should a JD include salary?", "Yes - posts with a salary range get noticeably more and better-matched applicants, and in many places it is becoming a legal requirement. Even a range helps."],
                 ["Can this write the JD for me instead?", "Yes - use our JD Builder to generate a complete job description from a few answers, then check it here if you like."]],
    },
}


HRDOC_BODY = """
<section class="page-hero"><div class="container">
  <span class="tag live">HR Documents</span>
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
    <div class="success-panel" id="successBox" style="display:none;margin-top:18px;border-top:1px solid var(--line);padding-top:18px"></div>
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
    window.nexoraSuccess("successBox", {
      heading: "Done! Your document is downloading",
      message: "Edit it freely in Word or Google Docs - and send Nexora to a friend who needs it.",
      next: [["/hr/calculators", "HR Calculators"],
             ["/career/resume-builder", "Resume Builder"],
             ["/document-ai", "Document AI"],
             ["/pdf/merge", "Merge PDF"]],
      shareText: "I just created an HR document with Nexora - free, no sign-up. Try it: ",
      path: "/hr/documents"
    });
  }).catch(function (e) { err.textContent = e.message || "Something went wrong."; });
}
buildTabs();
buildForm();
</script>
""" + SUCCESS_JS


LOGIN_BODY = """
<section class="page-hero"><div class="container">
  <h1>Sign in to Nexora</h1>
  <p>Free tools never need an account. Sign in is only needed for paid
  features and for saving your work.</p>
</div></section>
<section class="section"><div class="container" style="max-width:480px">
  <div class="card" style="text-align:center;padding:36px 28px">
    __ERR__
    __MSG__
    <div class="t-icon" style="font-size:40px;margin-bottom:10px">&#x1F512;</div>
    <h2 style="margin:0 0 8px">One click with Google</h2>
    <p style="margin:0 0 20px">Use your Google account to sign in - no new
    password to remember.</p>
    __GOOGLE__
    <div style="display:flex;align-items:center;gap:12px;margin:22px 0;color:var(--muted);font-size:13px">
      <span style="flex:1;border-top:1px solid var(--line)"></span>or with email<span style="flex:1;border-top:1px solid var(--line)"></span>
    </div>
    <form method="post" action="/auth/email" style="text-align:left">
      __NEXT__
      <div class="field"><label>Email</label>
        <input name="email" type="email" required placeholder="you@example.com"></div>
      <div class="field"><label>Password</label>
        <input name="password" type="password" required minlength="6" placeholder="At least 6 characters"></div>
      <div style="display:flex;gap:10px">
        <button class="btn" type="submit" name="mode" value="login" style="flex:1">Sign in</button>
        <button class="btn ghost" type="submit" name="mode" value="signup" style="flex:1">Create account</button>
      </div>
    </form>
  </div>
</div></section>
"""

PREMIUM_BODY = """
<section class="section" style="padding-top:0"><div class="container" style="max-width:780px">
  <div class="card" id="premcard" style="display:none;border:1.5px solid rgba(124,58,237,.35);background:linear-gradient(180deg,#fdfbff 0%,#ffffff 100%);box-shadow:0 8px 26px rgba(124,58,237,.12)">
    <span class="tag featured">Premium</span>
    <h2 style="margin:10px 0 6px" id="prem-name"></h2>
    <p id="prem-blurb" style="color:var(--muted);margin:0 0 16px"></p>
    <button class="btn" id="prem-buy" type="button"></button>
    <span id="prem-msg" style="margin-left:12px;font-size:13.5px;color:var(--muted)"></span>
    <div id="prem-panel" style="display:none;margin-top:20px;text-align:left">
      <div class="field"><label id="prem-srclabel"></label>
        <textarea id="prem-src" placeholder="Paste the text here" style="min-height:150px"></textarea></div>
      <div class="field"><label>Anything to emphasize? (optional)</label>
        <input id="prem-target" placeholder="e.g. target role, your concerns, company context"></div>
      <button class="btn" id="prem-run" type="button">Generate my result</button>
      <span id="prem-spin" style="display:none;margin-left:12px;font-size:14px;color:var(--muted)"><span class="spin"></span> The AI is working - this can take up to a minute...</span>
    </div>
    <div class="result" id="prem-result" style="display:none;text-align:left"></div>
    <div id="prem-dl" style="display:none;margin-top:14px;text-align:left">
      <button class="btn ghost" id="prem-docx" type="button">Download as Word (.docx)</button>
    </div>
  </div>
</div></section>
<script>
(function () {
  var PC = __PCFG__;
  var card = document.getElementById("premcard");
  var buy = document.getElementById("prem-buy");
  var msg = document.getElementById("prem-msg");
  var panel = document.getElementById("prem-panel");
  var result = document.getElementById("prem-result");
  var dl = document.getElementById("prem-dl");
  var lastResult = "";
  function setMsg(t) { msg.textContent = t || ""; }
  function goLogin() {
    location.href = "/login?next=" + encodeURIComponent(location.pathname);
  }
  function loadRzp(cb) {
    if (window.Razorpay) { cb(); return; }
    var s = document.createElement("script");
    s.src = "https://checkout.razorpay.com/v1/checkout.js";
    s.onload = cb;
    s.onerror = function () { setMsg("Could not load the payment window. Check your connection and try again."); };
    document.body.appendChild(s);
  }
  fetch("/api/config").then(function (r) { return r.json(); }).then(function (cfg) {
    if (!cfg.payments_ready) return;
    card.style.display = "block";
    document.getElementById("prem-name").textContent = PC.name;
    document.getElementById("prem-blurb").textContent = PC.blurb;
    document.getElementById("prem-srclabel").textContent =
      "Paste " + PC.sourceLabel;
    buy.textContent = "Unlock for \u20B9" + PC.price + " - one payment";
  }).catch(function () {});
  buy.onclick = function () {
    setMsg("");
    fetch("/api/me").then(function (r) { return r.json(); }).then(function (me) {
      if (!me.authenticated) { goLogin(); return; }
      buy.disabled = true; setMsg("Starting secure checkout...");
      fetch("/api/pay/order", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({product: PC.product})
      }).then(function (r) { return r.json(); }).then(function (o) {
        buy.disabled = false;
        if (o.login) { goLogin(); return; }
        if (o.error) { setMsg(o.error); return; }
        setMsg("");
        loadRzp(function () {
          var rzp = new Razorpay({
            key: o.key_id, amount: o.amount, currency: o.currency,
            order_id: o.order_id, name: "Nexora", description: o.name,
            prefill: {email: o.email}, theme: {color: "#7c3aed"},
            modal: {ondismiss: function () { setMsg("Payment cancelled - nothing was charged."); }},
            handler: function (resp) {
              setMsg("Verifying payment...");
              fetch("/api/pay/verify", {
                method: "POST", headers: {"Content-Type": "application/json"},
                body: JSON.stringify(resp)
              }).then(function (r) { return r.json(); }).then(function (v) {
                if (v.ok) {
                  buy.style.display = "none";
                  setMsg("Unlocked - your result is one step away.");
                  panel.style.display = "block";
                } else {
                  setMsg(v.error || "Verification failed. If money was deducted it is refunded automatically.");
                }
              }).catch(function () { setMsg("Network error while verifying. If money was deducted it is refunded automatically."); });
            }
          });
          rzp.open();
        });
      }).catch(function () { buy.disabled = false; setMsg("Network error. Please try again."); });
    }).catch(function () {});
  };
  document.getElementById("prem-run").onclick = function () {
    var src = document.getElementById("prem-src").value.trim();
    if (src.length < 40) { setMsg("Please paste " + PC.sourceLabel + " first."); return; }
    var run = document.getElementById("prem-run");
    run.disabled = true;
    document.getElementById("prem-spin").style.display = "inline";
    result.style.display = "none"; dl.style.display = "none"; setMsg("");
    fetch("/api/premium/" + PC.product, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        source_text: src,
        target: document.getElementById("prem-target").value
      })
    }).then(function (r) { return r.json(); }).then(function (v) {
      run.disabled = false;
      document.getElementById("prem-spin").style.display = "none";
      if (v.error) { setMsg(v.error); return; }
      lastResult = v.result;
      panel.style.display = "none";
      result.style.display = "block";
      result.textContent = v.result;
      dl.style.display = "block";
      buy.style.display = "";
      buy.textContent = "Unlock another run for \u20B9" + PC.price;
      setMsg("Done! Your result is below.");
    }).catch(function () {
      run.disabled = false;
      document.getElementById("prem-spin").style.display = "none";
      setMsg("Network error. Your credit was not used - please try again.");
    });
  };
  document.getElementById("prem-docx").onclick = function () {
    if (!lastResult) return;
    fetch("/api/download-docx", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({title: PC.name, content: lastResult})
    }).then(function (r) { return r.ok ? r.blob() : null; }).then(function (blob) {
      if (!blob) { setMsg("Could not create the Word file. Please try again."); return; }
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = PC.product + ".docx";
      document.body.appendChild(a); a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 800);
    });
  };
})();
</script>
"""


PDF_TOOL_BODY = r"""
<section class="page-hero"><div class="container">
  <span class="tag live">PDF Tools</span>
  <h1 style="margin-top:12px">__TITLE__</h1>
  <p>__DESC__ Free, unlimited and private - files are processed in memory
  and never stored.</p>
</div></section>

<section class="section"><div class="container" style="max-width:820px">
  <div class="card" style="padding:26px">
    <div class="dropzone" id="dz" role="button" tabindex="0" aria-label="Upload">
      <span style="color:var(--accent)">__UPLOAD_ICON__</span>
      <h3 id="dzTitle">Drop your file here, or tap to choose</h3>
      <p id="dzHint">__HINT__</p>
    </div>
    <input type="file" id="fileInput" hidden accept="__ACCEPT__" __MULTI__>
    <div id="fileList" style="margin-top:10px"></div>
    <div id="optArea" style="margin-top:16px"></div>
    <div class="err" id="errBox" style="margin-top:10px"></div>
    <button class="btn" id="goBtn" type="button" style="margin-top:16px;width:100%">
      __TITLE__</button>
    <div class="success-panel" id="doneBox" style="display:none;margin-top:6px"></div>
  </div>
  <p style="text-align:center;margin-top:14px;font-size:13px;opacity:.65">
    <a href="/" style="color:inherit">&larr; All 30 PDF tools on the home page</a>
  </p>
</div></section>

<script>
(function () {
  var CFG = __CFG_JSON__;
  var dz = document.getElementById('dz'),
      input = document.getElementById('fileInput'),
      list = document.getElementById('fileList'),
      err = document.getElementById('errBox'),
      go = document.getElementById('goBtn'),
      doneBox = document.getElementById('doneBox'),
      files = [];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; });
  }
  function renderFiles() {
    list.innerHTML = files.map(function (f, i) {
      return '<div style="display:flex;align-items:center;gap:10px;padding:8px 4px;'
        + 'border-bottom:1px solid rgba(15,23,42,.06)">'
        + '<span style="font-weight:600;flex:1;word-break:break-all">'
        + esc(f.name) + '</span>'
        + '<span style="opacity:.6;font-size:13px">'
        + (f.size / 1024).toFixed(0) + ' KB</span>'
        + '<button type="button" data-i="' + i + '" class="rm" '
        + 'style="border:0;background:none;color:#c00;cursor:pointer;font-size:16px">'
        + '&times;</button></div>';
    }).join('');
    list.querySelectorAll('.rm').forEach(function (b) {
      b.addEventListener('click', function () {
        files.splice(+b.getAttribute('data-i'), 1); renderFiles();
      });
    });
  }
  function addFiles(fl) {
    for (var i = 0; i < fl.length; i++) {
      if (!CFG.multiple && files.length >= 1) files = [];
      files.push(fl[i]);
      if (!CFG.multiple) break;
    }
    renderFiles();
  }
  dz.addEventListener('click', function () { input.click(); });
  dz.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.click(); }
  });
  input.addEventListener('change', function () { addFiles(input.files); input.value = ''; });
  dz.addEventListener('dragover', function (e) { e.preventDefault(); });
  dz.addEventListener('drop', function (e) {
    e.preventDefault(); addFiles(e.dataTransfer.files);
  });

  var optArea = document.getElementById('optArea');
  optArea.innerHTML = CFG.options.map(function (o) {
    if (o.kind === 'select') {
      return '<label class="field" style="display:block;margin-top:10px;font-weight:600;font-size:14px">'
        + esc(o.label) + '<select id="opt_' + esc(o.key) + '" '
        + 'style="margin-top:6px">'
        + o.choices.map(function (c) {
            return '<option value="' + esc(c[0]) + '">' + esc(c[1]) + '</option>';
          }).join('') + '</select></label>';
    }
    return '<label class="field" style="display:block;margin-top:10px;font-weight:600;font-size:14px">'
      + esc(o.label) + '<input id="opt_' + esc(o.key) + '" '
      + 'style="margin-top:6px" placeholder="' + esc(o.ph || '') + '"></label>';
  }).join('');

  go.addEventListener('click', function () {
    err.textContent = '';
    if (!files.length) { err.textContent = 'Please choose a file first.'; return; }
    var fd = new FormData();
    files.forEach(function (f) { fd.append('files', f, f.name); });
    CFG.options.forEach(function (o) {
      var el = document.getElementById('opt_' + o.key);
      if (el) fd.append(o.key, el.value);
    });
    go.disabled = true;
    go.innerHTML = '<span class="spin"></span> Working...';
    fetch('/api/pdf/' + CFG.slug, { method: 'POST', body: fd })
      .then(function (r) {
        var ct = r.headers.get('content-type') || '';
        if (!r.ok || ct.indexOf('json') !== -1) {
          return r.json().then(function (j) {
            throw new Error(j.error || 'Something went wrong. Please try again.');
          });
        }
        var cd = r.headers.get('content-disposition') || '';
        var m = cd.match(/filename="?([^";]+)"?/);
        var fname = m ? m[1] : 'download';
        return r.blob().then(function (b) {
          var url = URL.createObjectURL(b);
          var a = document.createElement('a');
          a.href = url; a.download = fname;
          document.body.appendChild(a); a.click(); a.remove();
          dz.style.display = 'none';
          list.style.display = 'none';
          optArea.style.display = 'none';
          err.style.display = 'none';
          go.style.display = 'none';
          window.nexoraSuccess(doneBox, {
            heading: 'Done! Your file is ready',
            message: CFG.title + ' completed - your download started automatically.',
            download: { url: url, name: fname, label: fname },
            next: CFG.next || [],
            shareText: CFG.share || ('I just used Nexora ' + CFG.title + ' - free, no sign-up. Try it: '),
            path: '/pdf/' + CFG.slug
          });
          var again = document.createElement('button');
          again.className = 'btn ghost';
          again.type = 'button';
          again.style.marginTop = '18px';
          again.textContent = 'Process another file';
          again.addEventListener('click', function () {
            files = [];
            renderFiles();
            doneBox.style.display = 'none';
            doneBox.innerHTML = '';
            dz.style.display = '';
            list.style.display = '';
            optArea.style.display = '';
            err.style.display = '';
            go.style.display = '';
            window.scrollTo({ top: 0, behavior: 'smooth' });
          });
          doneBox.appendChild(again);
        });
      })
      .catch(function (e) { err.textContent = e.message; })
      .finally(function () {
        go.disabled = false; go.textContent = CFG.title;
      });
  });
})();
</script>
""" + SUCCESS_JS
