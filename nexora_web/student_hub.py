"""Nexora Students hub: free study tools for Indian students.

All calculators run in the browser (nothing is sent or stored). The formulas
live once in FORMULAS_JS and are mirrored in Python (below) so tests can check
both give the same answers. install() adds routes, the nav link and sitemap
paths to the main app without touching its other code.
"""
import math

SITE = "https://nexora-web-q7rn.onrender.com"

# ---------------------------------------------------------------- formulas (python mirror)


def percentage(obtained, maximum):
    return obtained / maximum * 100 if maximum > 0 else None


def attendance_status(attended, total, required_pct):
    """-> (current %, classes to attend in a row to reach required, classes you can still miss)"""
    r = required_pct / 100.0
    if total <= 0 or r <= 0 or r >= 1:
        return None
    cur = attended / total
    if cur >= r - 1e-12:
        return cur * 100, 0, int(math.floor(attended / r - total + 1e-9))
    return cur * 100, int(math.ceil((r * total - attended) / (1 - r) - 1e-9)), 0


def final_marks_needed(parts, target_pct, final_weight, final_max):
    """parts = [(score, max, weight)] done so far. Weights are % of the whole course.
    -> (needed % in the final, needed marks out of final_max)"""
    done = sum(s / m * w for s, m, w in parts)
    need_pct = (target_pct - done) / final_weight * 100
    return need_pct, need_pct * final_max / 100


def gpa(rows):
    tc = sum(c for c, _ in rows)
    return sum(c * g for c, g in rows) / tc if tc else None


CONVERT = {"vtu": (lambda c: (c - 0.75) * 10, lambda p: p / 10 + 0.75),
           "x10": (lambda c: c * 10, lambda p: p / 10),
           "x95": (lambda c: c * 9.5, lambda p: p / 9.5),
           "m05": (lambda c: (c - 0.5) * 10, lambda p: p / 10 + 0.5)}

# ---------------------------------------------------------------- shared JS / CSS

FORMULAS_JS = r"""
function r2(x){return Math.round(x*100)/100;}
function hubPct(o,m){return m>0?o/m*100:null;}
function hubAttend(a,t,rp){var r=rp/100;if(t<=0||r<=0||r>=1)return null;var cur=a/t;
  if(cur>=r-1e-12)return {cur:cur*100,need:0,miss:Math.floor(a/r-t+1e-9)};
  return {cur:cur*100,need:Math.ceil((r*t-a)/(1-r)-1e-9),miss:0};}
function hubFinal(parts,target,fw,fmax){var d=0;parts.forEach(function(p){d+=p[0]/p[1]*p[2];});
  var np=(target-d)/fw*100;return {done:d,needPct:np,needMarks:np*fmax/100};}
function hubGpa(rows){var tc=0,cp=0;rows.forEach(function(r){tc+=r[0];cp+=r[0]*r[1];});
  return {credits:tc,points:cp,gpa:tc>0?cp/tc:null};}
var HUB_CONV={vtu:[function(c){return (c-0.75)*10},function(p){return p/10+0.75}],
  x10:[function(c){return c*10},function(p){return p/10}],
  x95:[function(c){return c*9.5},function(p){return p/9.5}],
  m05:[function(c){return (c-0.5)*10},function(p){return p/10+0.5}]};
"""

COMMON_JS = r"""
function $(id){return document.getElementById(id);}
function num(id){var v=$(id).value;return v===""?NaN:Number(v);}
function err(m){$("hub_err").textContent=m||"";}
function out(h){$("hub_out").innerHTML=h;}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
function rmRow(b){b.parentNode.remove();}
"""

CSS = """<style>
.sc-row{display:flex;gap:8px;margin-bottom:10px;align-items:center;flex-wrap:wrap}
.sc-row input,.sc-row select,.sc-box input,.sc-box select{padding:11px 12px;border:1px solid #d9d6ee;border-radius:10px;font-size:16px;min-width:0;max-width:100%;background:#fff;box-sizing:border-box}
.sc-row input.sc-n{flex:2 1 120px}.sc-row input.sc-a,.sc-row input.sc-b{flex:1 1 80px}.sc-row select{flex:1 1 110px}
.sc-x{border:0;background:#f3f1fb;border-radius:10px;padding:10px 12px;cursor:pointer;font-size:16px}
.sc-res{margin-top:16px;padding:16px;border-radius:14px;background:linear-gradient(135deg,#f3efff,#ffeef7)}
.sc-res b.big{font-size:2rem;display:block}
.sc-res table{width:100%;border-collapse:collapse;margin-top:8px}.sc-res td{padding:6px 0;border-top:1px solid #e6e1f7}
.sc-box label{display:block;margin:10px 0 4px;font-weight:600}
.sc-box input.full,.sc-box select.full{width:100%}
.sc-two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.hub-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.hub-h{margin:28px 0 12px;font-size:1.3rem}
@media(max-width:560px){.sc-row input.sc-n{flex:1 1 100%}.sc-two{grid-template-columns:1fr}}
</style>"""


def _hero(h1, p):
    return ('<section class="page-hero"><div class="container"><span class="tag live">Free student tool</span>'
            f'<h1 style="margin-top:12px">{h1}</h1><p>{p}</p></div></section>')


def _wrap(inner):
    return ('<section class="section"><div class="container" style="max-width:780px"><div class="card sc-box">'
            + inner + '<div class="err" id="hub_err"></div><div id="hub_out"></div></div></div></section>')


def _script(js):
    return "<script>" + COMMON_JS + FORMULAS_JS + js + "</script>"


# ---------------------------------------------------------------- tool bodies

PERCENT_BODY = CSS + _hero("Percentage Calculator for Marks", "Enter marks for each subject. Get total, percentage and class. Works for school, PUC, diploma and degree marks. Nothing is stored.") + _wrap("""
<div id="rows"></div>
<div class="toolbar"><button class="btn ghost" type="button" onclick="addRow()">+ Add subject</button>
<button class="btn" type="button" onclick="run()">Calculate</button></div>
<div class="hint">Leave a row empty to skip it. Enter the maximum marks for each subject (100, 50, 25 and so on).</div>""") + _script(r"""
function addRow(){var d=document.createElement("div");d.className="sc-row";
 d.innerHTML='<input class="sc-n" placeholder="Subject (optional)"><input class="sc-a" type="number" min="0" step="any" inputmode="decimal" placeholder="Marks"><input class="sc-b" type="number" min="0" step="any" inputmode="decimal" placeholder="Out of" value="100"><button type="button" class="sc-x" onclick="rmRow(this)" aria-label="Remove">x</button>';
 $("rows").appendChild(d);}
function cls(p){return p>=75?"Distinction":p>=60?"First class":p>=50?"Second class":p>=40?"Pass class":"Below pass mark";}
function run(){err("");var o=0,m=0,n=0,bad=false;
 document.querySelectorAll("#rows .sc-row").forEach(function(r){var a=r.querySelector(".sc-a").value,b=r.querySelector(".sc-b").value;
  if(a==="")return;if(b===""||Number(b)<=0||Number(a)<0||Number(a)>Number(b)){bad=true;return;}o+=Number(a);m+=Number(b);n++;});
 if(bad){err("Check each row: marks must be between 0 and the maximum.");return;}
 if(!n){err("Enter marks for at least one subject.");return;}
 var p=hubPct(o,m);
 out('<div class="sc-res"><b class="big">'+r2(p).toFixed(2)+'%</b><table><tr><td>Total marks</td><td>'+o+' / '+m+'</td></tr><tr><td>Subjects counted</td><td>'+n+'</td></tr><tr><td>Class (common scale)</td><td>'+cls(p)+'</td></tr></table></div>');}
for(var i=0;i<6;i++)addRow();""")

ATTEND_BODY = CSS + _hero("Attendance Calculator", "Find your attendance percentage, how many classes you must attend to reach 75% (or your college limit), and how many you can still miss.") + _wrap("""
<div class="sc-two"><div><label for="a">Classes attended</label><input class="full" id="a" type="number" min="0" step="1" inputmode="numeric"></div>
<div><label for="t">Total classes held</label><input class="full" id="t" type="number" min="0" step="1" inputmode="numeric"></div></div>
<label for="r">Required attendance (%)</label><input class="full" id="r" type="number" min="1" max="99" step="any" value="75" inputmode="decimal">
<div class="toolbar"><button class="btn" type="button" onclick="run()">Check attendance</button></div>
<div class="hint">Most colleges ask for 75%. Some ask for 80% or 85% for exams or scholarships, so change the box if yours is different.</div>""") + _script(r"""
function run(){err("");var a=num("a"),t=num("t"),r=num("r");
 if(isNaN(a)||isNaN(t)||isNaN(r)||a<0||t<=0||a>t){err("Enter classes attended (not more than total classes) and total classes held.");return;}
 var x=hubAttend(a,t,r);if(!x){err("Required attendance must be between 1 and 99.");return;}
 var h='<div class="sc-res"><b class="big">'+r2(x.cur).toFixed(2)+'%</b><table><tr><td>Attended / held</td><td>'+a+' / '+t+'</td></tr>';
 if(x.need>0){h+='<tr><td>Status</td><td>Below '+r+'%</td></tr><tr><td>Classes to attend in a row</td><td><b>'+x.need+'</b></td></tr><tr><td>Attendance after that</td><td>'+r2((a+x.need)/(t+x.need)*100).toFixed(2)+'%</td></tr>';}
 else{h+='<tr><td>Status</td><td>At or above '+r+'%</td></tr><tr><td>Classes you can still miss</td><td><b>'+x.miss+'</b></td></tr>';}
 out(h+'</table></div>');}""")

FINAL_BODY = CSS + _hero("Marks Needed in the Final Exam Calculator", "Enter your internal or test marks so far and the target you want. See the score you need in the final exam.") + _wrap("""
<div id="rows"></div>
<div class="toolbar"><button class="btn ghost" type="button" onclick="addRow()">+ Add component</button></div>
<div class="sc-two"><div><label for="fw">Final exam weight (% of course)</label><input class="full" id="fw" type="number" min="1" max="100" step="any" value="60" inputmode="decimal"></div>
<div><label for="fm">Final exam maximum marks</label><input class="full" id="fm" type="number" min="1" step="any" value="100" inputmode="decimal"></div></div>
<label for="tg">Target overall score (%)</label><input class="full" id="tg" type="number" min="1" max="100" step="any" value="60" inputmode="decimal">
<div class="toolbar"><button class="btn" type="button" onclick="run()">Find marks needed</button></div>
<div class="hint">Weights are the share of the course total. Example: internals 40% and final 60%. Component weights plus the final weight should add up to 100.</div>""") + _script(r"""
function addRow(){var d=document.createElement("div");d.className="sc-row";
 d.innerHTML='<input class="sc-n" placeholder="Component (e.g. Internals)"><input class="sc-a" type="number" min="0" step="any" inputmode="decimal" placeholder="Score"><input class="sc-b" type="number" min="0" step="any" inputmode="decimal" placeholder="Out of"><input class="sc-b sc-w" type="number" min="0" step="any" inputmode="decimal" placeholder="Weight %"><button type="button" class="sc-x" onclick="rmRow(this)" aria-label="Remove">x</button>';
 $("rows").appendChild(d);}
function run(){err("");var parts=[],bad=false,ws=0;
 document.querySelectorAll("#rows .sc-row").forEach(function(r){var i=r.querySelectorAll("input"),s=i[1].value,m=i[2].value,w=i[3].value;
  if(s===""&&m===""&&w==="")return;if(s===""||m===""||w===""||Number(m)<=0||Number(s)<0||Number(s)>Number(m)||Number(w)<0){bad=true;return;}
  parts.push([Number(s),Number(m),Number(w)]);ws+=Number(w);});
 var fw=num("fw"),fm=num("fm"),tg=num("tg");
 if(bad||isNaN(fw)||isNaN(fm)||isNaN(tg)||fw<=0||fm<=0){err("Fill every box in each row, and check the final exam weight and maximum.");return;}
 var x=hubFinal(parts,tg,fw,fm),note="";
 if(Math.abs(ws+fw-100)>0.01)note='<div class="hint">Your weights add up to '+r2(ws+fw)+', not 100. The answer assumes the final carries '+fw+'% of the course.</div>';
 var msg=x.needPct<=0?"You already meet the target.":x.needPct>100?"The target is out of reach: it needs more than full marks in the final.":"";
 out('<div class="sc-res"><b class="big">'+(x.needPct<=0?"0":r2(x.needMarks).toFixed(2))+' / '+fm+'</b><table><tr><td>Needed in final</td><td>'+(x.needPct<=0?"0":r2(x.needPct).toFixed(2))+'%</td></tr><tr><td>Already earned</td><td>'+r2(x.done).toFixed(2)+' of '+r2(100-fw)+' points</td></tr></table>'+(msg?'<p><b>'+msg+'</b></p>':'')+note+'</div>');}
addRow();addRow();""")

GPA_BODY = CSS + _hero("GPA Calculator with Your Own Grade Scale", "Works for any university or college. Pick a 10-point or 4-point scale, or type your own grade points, then add subjects with credits.") + _wrap("""
<label for="scale">Grade scale</label>
<select class="full" id="scale" onchange="setScale()"><option value="10">10-point (O 10, A+ 9, A 8, B+ 7, B 6, C 5, F 0)</option><option value="vtu">VTU style (S 10, A 9, B 8, C 7, D 6, E 4, F 0)</option><option value="4">4-point (A 4, B 3, C 2, D 1, F 0)</option></select>
<div style="height:10px"></div><div id="rows"></div>
<div class="toolbar"><button class="btn ghost" type="button" onclick="addRow()">+ Add subject</button><button class="btn" type="button" onclick="run()">Calculate GPA</button></div>
<div class="hint">You can also pick a grade and then edit the "Points" box if your college uses different values. The result is credits x points added up, divided by total credits.</div>""") + _script(r"""
var SC={"10":[["O",10],["A+",9],["A",8],["B+",7],["B",6],["C",5],["F",0]],"vtu":[["S",10],["A",9],["B",8],["C",7],["D",6],["E",4],["F",0]],"4":[["A",4],["B",3],["C",2],["D",1],["F",0]]};
function opts(){var o='<option value="">Grade</option>';SC[$("scale").value].forEach(function(g){o+='<option value="'+g[1]+'">'+g[0]+'</option>';});return o;}
function addRow(){var d=document.createElement("div");d.className="sc-row";
 d.innerHTML='<input class="sc-n" placeholder="Subject (optional)"><input class="sc-a" type="number" min="0" step="0.5" inputmode="decimal" placeholder="Credits"><select onchange="this.nextSibling.value=this.value">'+opts()+'</select><input class="sc-b" type="number" min="0" step="any" inputmode="decimal" placeholder="Points"><button type="button" class="sc-x" onclick="rmRow(this)" aria-label="Remove">x</button>';
 $("rows").appendChild(d);}
function setScale(){document.querySelectorAll("#rows .sc-row").forEach(function(r){var s=r.querySelector("select");s.innerHTML=opts();r.querySelector(".sc-b").value="";});}
function run(){err("");var rows=[],bad=false;
 document.querySelectorAll("#rows .sc-row").forEach(function(r){var i=r.querySelectorAll("input"),c=i[1].value,p=i[2].value;
  if(c===""&&p==="")return;if(c===""||p===""||Number(c)<0||Number(p)<0){bad=true;return;}rows.push([Number(c),Number(p)]);});
 if(bad){err("Each subject needs credits and points (pick a grade or type points).");return;}
 var g=hubGpa(rows);if(g.gpa===null){err("Add at least one subject with credits.");return;}
 out('<div class="sc-res"><b class="big">GPA '+r2(g.gpa).toFixed(2)+'</b><table><tr><td>Total credits</td><td>'+g.credits+'</td></tr><tr><td>Total credit points</td><td>'+g.points+'</td></tr><tr><td>Formula</td><td>'+g.points+' / '+g.credits+'</td></tr></table></div>');}
for(var i=0;i<6;i++)addRow();""")

CONVERT_BODY = CSS + _hero("CGPA to Percentage and Percentage to CGPA", "Convert both ways with the rule your university uses. Pick the formula, type a value, see the result.") + _wrap("""
<label for="f">Formula</label>
<select class="full" id="f"><option value="vtu">(CGPA - 0.75) x 10 (VTU, JNTUH style)</option><option value="m05">(CGPA - 0.5) x 10 (JNTU-ACEP style)</option><option value="x10">CGPA x 10 (simple)</option><option value="x95">CGPA x 9.5 (CBSE style)</option></select>
<div class="sc-two"><div><label for="cg">CGPA (0 to 10)</label><input class="full" id="cg" type="number" min="0" max="10" step="any" inputmode="decimal"></div>
<div><label for="pc">Percentage (0 to 100)</label><input class="full" id="pc" type="number" min="0" max="100" step="any" inputmode="decimal"></div></div>
<div class="toolbar"><button class="btn" type="button" onclick="run('cg')">CGPA to %</button><button class="btn ghost" type="button" onclick="run('pc')">% to CGPA</button></div>
<div class="hint">These rules are published by some universities only for certain schemes. Your own university or the employer decides which one counts, so check before you quote it.</div>""") + _script(r"""
function run(from){err("");var f=HUB_CONV[$("f").value];
 if(from==="cg"){var c=num("cg");if(isNaN(c)||c<0||c>10){err("Enter a CGPA between 0 and 10.");return;}var p=f[0](c);if(p<0)p=0;
  $("pc").value=r2(p).toFixed(2);out('<div class="sc-res"><b class="big">'+r2(p).toFixed(2)+'%</b>CGPA '+c+' converted with the selected formula.</div>');}
 else{var q=num("pc");if(isNaN(q)||q<0||q>100){err("Enter a percentage between 0 and 100.");return;}var g=f[1](q);if(g>10)g=10;
  $("cg").value=r2(g).toFixed(2);out('<div class="sc-res"><b class="big">CGPA '+r2(g).toFixed(2)+'</b>'+q+'% converted with the selected formula.</div>');}}""")

TOOLS = {
    "percentage-calculator": dict(
        name="Percentage Calculator", icon="%", short="Total marks and percentage across subjects.",
        title="Percentage Calculator for Marks - Free | Nexora",
        meta="Free marks percentage calculator for school, PUC, diploma and degree students. Add subject marks, get total, percentage and class instantly.",
        body=PERCENT_BODY,
        faq=[["How do I calculate percentage from marks?", "Add all marks you scored, add all maximum marks, divide the first by the second and multiply by 100."],
             ["Can I use different maximum marks for each subject?", "Yes. Type the maximum for each subject in the Out of box. Lab and theory papers can differ."]]),
    "attendance-calculator": dict(
        name="Attendance Calculator", icon="75", short="Check 75% attendance and bunk-safe classes.",
        title="Attendance Calculator - 75% Attendance Check | Nexora",
        meta="Free attendance calculator for students. Find your attendance percentage, classes needed to reach 75%, and how many classes you can still miss.",
        body=ATTEND_BODY,
        faq=[["How is attendance percentage calculated?", "Classes attended divided by total classes held, multiplied by 100."],
             ["How many classes do I need to attend to reach 75%?", "If you attend the next x classes without missing any, attendance becomes (attended + x) divided by (held + x). The tool finds the smallest x that reaches your target."]]),
    "final-marks-needed-calculator": dict(
        name="Marks Needed in Final", icon="?", short="Score you need in the final exam to hit your target.",
        title="What Do I Need in the Final Exam? Marks Calculator | Nexora",
        meta="Free calculator: enter internal marks and a target score to see the marks you need in the final exam. Weighted grade calculator for students.",
        body=FINAL_BODY,
        faq=[["How do I find the marks needed in the final?", "Work out the points you already earned (score divided by maximum, times weight). Subtract from your target, divide by the final exam weight and multiply by the final maximum."],
             ["What if the answer is above 100%?", "Then the target cannot be reached with the final alone. Lower the target or ask about improvement or revaluation options."]]),
    "gpa-calculator": dict(
        name="GPA Calculator", icon="GPA", short="Credit-weighted GPA on a 10-point, VTU or 4-point scale.",
        title="GPA Calculator - 10 Point and 4 Point Scale | Nexora",
        meta="Free GPA and SGPA calculator for any college. Choose a 10-point, VTU or 4-point grade scale, add credits and grades, and get your GPA.",
        body=GPA_BODY,
        faq=[["How is GPA calculated?", "Multiply each subject's credits by its grade points, add them up, and divide by the total credits."],
             ["My college uses different grade points.", "Pick any grade, then type your own value in the Points box. The tool uses what is in that box."]]),
    "cgpa-percentage-converter": dict(
        name="CGPA / Percentage Converter", icon="CG", short="Convert CGPA to percentage and back, four formulas.",
        title="CGPA to Percentage and Percentage to CGPA Converter | Nexora",
        meta="Free converter for CGPA to percentage and percentage to CGPA. Choose the (CGPA-0.75)x10, (CGPA-0.5)x10, CGPAx10 or CGPAx9.5 formula.",
        body=CONVERT_BODY,
        faq=[["Which CGPA to percentage formula should I use?", "Use the one your university states. VTU publishes (CGPA - 0.75) x 10 for some schemes, and CBSE uses CGPA x 9.5 for its 10-point grades. When unsure, ask your university office."],
             ["Is the result official?", "No. It is an estimate for forms and planning."]]),
}

# Tools in the hub, grouped. Entries are (href, title, description).
LINK_GROUPS = [
    ("Marks, grades and attendance", [("/students/" + k, v["name"], v["short"]) for k, v in TOOLS.items()] + [
        ("/vtu-sgpa-calculator", "VTU SGPA Calculator", "Semester SGPA from credits and grades."),
        ("/vtu-cgpa-calculator", "VTU CGPA Calculator", "CGPA across semesters, lateral entry too."),
        ("/cgpa-to-percentage-calculator", "CGPA to Percentage (VTU)", "VTU formula with a simple option.")]),
    ("PDF tools for assignments", [
        ("/pdf/merge", "Merge PDF", "Join notes and assignments into one file."),
        ("/pdf/compress", "Compress PDF", "Shrink a PDF to fit upload limits."),
        ("/pdf/jpg-to-pdf", "JPG to PDF", "Turn photos of handwritten pages into a PDF."),
        ("/pdf/scan-to-pdf", "Scan to PDF", "Make a clean PDF from phone photos."),
        ("/pdf/word-to-pdf", "Word to PDF", "Convert a report before you submit it."),
        ("/pdf/split", "Split PDF", "Pull out the pages you need.")]),
    ("Resume and career", [
        ("/resume-builder", "Resume Builder", "Build a fresher resume (Rs 99 per CV)."),
        ("/career/ats-optimizer", "ATS Resume Checker", "See if your resume passes job filters."),
        ("/career/cover-letter-builder", "Cover Letter Writer", "Write a cover letter for an internship or job.")]),
]


def all_paths():
    return ["/students"] + ["/students/" + k for k in TOOLS]


def hub_body():
    parts = [CSS, _hero("Nexora for Students", "Free tools for marks, grades, attendance, PDFs and your first resume. No sign-up needed. Everything runs in your browser.")]
    parts.append('<section class="section"><div class="container" style="max-width:1000px">')
    for title, items in LINK_GROUPS:
        parts.append(f'<h2 class="hub-h">{title}</h2><div class="hub-grid">')
        for href, t, d in items:
            parts.append(f'<a class="card card-link" href="{href}"><h3 style="margin-top:0">{t}</h3><p>{d}</p></a>')
        parts.append("</div>")
    parts.append("</div></section>")
    return "".join(parts)


def _tool_page(slug, page_fn):
    spec = TOOLS[slug]
    faqs = "".join(f"<h3 style='margin:18px 0 6px'>{q}</h3><p>{a}</p>" for q, a in spec["faq"])
    more = "".join(f'<a class="btn ghost" href="/students/{k}">{v["name"]}</a>' for k, v in TOOLS.items() if k != slug)
    extra = ('<section class="section" style="padding-top:0"><div class="container" style="max-width:780px">'
             f'<div class="card"><h2 style="margin-top:0">Common questions</h2>{faqs}</div>'
             '<div class="card"><h2 style="margin-top:0">More free student tools</h2><div style="display:flex;flex-wrap:wrap;gap:10px">'
             f'{more}<a class="btn ghost" href="/students">All student tools</a></div></div></div></section>')
    return page_fn(spec["title"].replace(" | Nexora", ""), spec["meta"], "/students", spec["body"] + extra)


def install(app, page_fn, nav_items):
    from fastapi.responses import HTMLResponse
    if not any(h == "/students" for h, _ in nav_items):
        nav_items.insert(1, ("/students", "Students"))

    @app.get("/students", response_class=HTMLResponse)
    async def students_hub() -> str:
        return page_fn("Free Student Tools - Marks, CGPA, Attendance, PDF",
                       "Free tools for Indian students: percentage, CGPA, SGPA and attendance calculators, PDF tools for assignments and a fresher resume builder.",
                       "/students", hub_body())

    @app.get("/students/{slug}", response_class=HTMLResponse)
    async def students_tool(slug: str) -> HTMLResponse:
        from fastapi import HTTPException
        if slug not in TOOLS:
            raise HTTPException(status_code=404, detail="Not found")
        return HTMLResponse(_tool_page(slug, page_fn))
