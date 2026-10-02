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


def word_stats(text):
    words = text.split()
    n = len(words)
    chars = len(text)
    nospace = len("".join(text.split()))
    import re
    sentences = len([x for x in re.split(r"[.!?]+", text) if x.strip()])
    paras = len([p for p in re.split(r"\n\s*\n", text) if p.strip()])
    return n, chars, nospace, sentences, paras


def mm_to_px(mm, dpi):
    return int(round(mm / 25.4 * dpi))


def gpa(rows):
    tc = sum(c for c, _ in rows)
    return sum(c * g for c, g in rows) / tc if tc else None


def study_plan(days_left, hours_per_day, weights, revision_days=0):
    """weights = list of positive numbers (difficulty). -> (study_days, [total hours per subject], [hours per day per subject])"""
    study_days = max(days_left - revision_days, 0)
    total = study_days * hours_per_day
    ws = sum(weights)
    tot = [total * w / ws for w in weights]
    per = [hours_per_day * w / ws for w in weights]
    return study_days, tot, per


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
function hubPlan(days,hpd,ws,rev){var sd=Math.max(days-rev,0),tot=sd*hpd,sum=0;ws.forEach(function(w){sum+=w;});
  return {sd:sd,tot:ws.map(function(w){return tot*w/sum;}),per:ws.map(function(w){return hpd*w/sum;})};}
function hubDays(a,b){return Math.round((Date.UTC(b.getFullYear(),b.getMonth(),b.getDate())-Date.UTC(a.getFullYear(),a.getMonth(),a.getDate()))/86400000);}
function hubWords(t){var w=t.split(/\s+/).filter(Boolean),n=w.length,ns=t.replace(/\s+/g,"").length,
  se=t.split(/[.!?]+/).filter(function(x){return x.trim();}).length,pa=t.split(/\n\s*\n/).filter(function(x){return x.trim();}).length;
  return {words:n,chars:t.length,nospace:ns,sentences:se,paras:pa};}
function hubMm(mm,dpi){return Math.round(mm/25.4*dpi);}
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
.sc-row input.sc-n{flex:2 1 120px}.sc-row input.sc-a,.sc-row input.sc-b{flex:1 1 80px}.sc-row select{flex:1 1 110px;width:auto}
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

COUNT_BODY = CSS + _hero("Exam Countdown Timer", "Add your exams and see the days and hours left for each one. Your list stays on this device only. Nothing is uploaded.") + _wrap("""
<div class="sc-row"><input class="sc-n" id="en" placeholder="Exam name (e.g. Maths paper 1)"><input class="sc-a" id="ed" type="datetime-local"><button class="btn" type="button" onclick="addExam()">Add exam</button></div>
<div id="list"></div>
<div class="hint">Saved in your browser on this device. Clearing browser data removes the list. Pick the exam start time so the hours are right.</div>""") + _script(r"""
var KEY="nexora_exams_v1";
function load(){try{return JSON.parse(localStorage.getItem(KEY)||"[]");}catch(e){return [];}}
function save(a){try{localStorage.setItem(KEY,JSON.stringify(a));}catch(e){}}
function addExam(){err("");var n=$("en").value.trim(),d=$("ed").value;if(!n||!d){err("Type the exam name and pick the date and time.");return;}
 var a=load();a.push({n:n,d:d});a.sort(function(x,y){return new Date(x.d)-new Date(y.d);});save(a);$("en").value="";render();}
function del(i){var a=load();a.splice(i,1);save(a);render();}
function render(){var a=load(),now=new Date(),h="";
 if(!a.length)h='<p class="hint">No exams yet. Add the first one above.</p>';
 a.forEach(function(x,i){var ms=new Date(x.d)-now,t;
  if(ms<=0)t="Started or over";else{var m=Math.floor(ms/60000),dd=Math.floor(m/1440),hh=Math.floor(m%1440/60),mm=m%60;t=dd+" days "+hh+" h "+mm+" min";}
  h+='<div class="sc-res" style="margin-top:10px"><b style="font-size:1.1rem">'+esc(x.n)+'</b><div>'+esc(new Date(x.d).toLocaleString([], {dateStyle:"medium",timeStyle:"short"}))+'</div><b class="big">'+t+'</b><button class="sc-x" type="button" onclick="del('+i+')">Remove</button></div>';});
 $("list").innerHTML=h;}
render();setInterval(render,30000);""")

PLAN_BODY = CSS + _hero("Study Planner: Hours per Subject Before Your Exam", "Enter your exam date, hours you can study each day and your subjects. Weak or heavy subjects get more time. Get a clear daily split.") + _wrap("""
<div class="sc-two"><div><label for="pd">Exam date</label><input class="full" id="pd" type="date"></div>
<div><label for="ph">Study hours per day</label><input class="full" id="ph" type="number" min="0.5" max="16" step="0.5" value="4" inputmode="decimal"></div></div>
<label for="pr">Keep last days for revision</label>
<select class="full" id="pr"><option value="0">None</option><option value="1">1 day</option><option value="2" selected>2 days</option><option value="3">3 days</option></select>
<div style="height:10px"></div><div id="rows"></div>
<div class="toolbar"><button class="btn ghost" type="button" onclick="addRow()">+ Add subject</button><button class="btn" type="button" onclick="run()">Make plan</button></div>
<div class="hint">Difficulty: 1 means easy for you, 5 means hard or heavy. A subject with 4 gets twice the time of a subject with 2.</div>""") + _script(r"""
function addRow(){var d=document.createElement("div");d.className="sc-row";
 d.innerHTML='<input class="sc-n" placeholder="Subject"><select class="sc-a"><option value="1">1 easy</option><option value="2">2</option><option value="3" selected>3 medium</option><option value="4">4</option><option value="5">5 hard</option></select><button type="button" class="sc-x" onclick="rmRow(this)" aria-label="Remove">x</button>';
 $("rows").appendChild(d);}
function run(){err("");var v=$("pd").value,hpd=num("ph"),rev=Number($("pr").value);
 if(!v||isNaN(hpd)||hpd<=0){err("Pick the exam date and the hours you can study per day.");return;}
 var p=v.split("-"),ex=new Date(Number(p[0]),Number(p[1])-1,Number(p[2])),days=hubDays(new Date(),ex);
 if(days<=0){err("Pick an exam date after today.");return;}
 var names=[],ws=[];document.querySelectorAll("#rows .sc-row").forEach(function(r,k){var n=r.querySelector(".sc-n").value.trim();if(!n&&k>=0&&r.querySelector(".sc-n").value==="")return;names.push(n);ws.push(Number(r.querySelector("select").value));});
 if(!names.length){err("Add at least one subject.");return;}
 var pl=hubPlan(days,hpd,ws,rev);
 if(pl.sd<=0){err("Not enough days: lower the revision days or pick a later date.");return;}
 var h='<div class="sc-res"><b class="big">'+days+' days left</b><div>'+pl.sd+' study days'+(rev?' + '+rev+' revision day'+(rev>1?'s':''):'')+', '+r2(pl.sd*hpd)+' study hours in total.</div><table><tr><td><b>Subject</b></td><td><b>Per day</b></td><td><b>Total</b></td></tr>';
 names.forEach(function(n,i){h+='<tr><td>'+esc(n)+'</td><td>'+r2(pl.per[i]).toFixed(2)+' h</td><td>'+r2(pl.tot[i]).toFixed(1)+' h</td></tr>';});
 out(h+'</table><div class="hint">Plan for a short break every hour. Use revision days for past papers and weak topics.</div></div>');}
addRow();addRow();addRow();addRow();""")

POMO_BODY = CSS + _hero("Pomodoro Study Timer", "Study in focused 25 minute blocks with short breaks. Change the times if you like. A soft beep tells you when to switch.") + _wrap("""
<div class="sc-res" style="text-align:center"><div id="mode" style="font-weight:600">Focus</div><b class="big" id="clock" style="font-size:3.4rem">25:00</b><div id="round" class="hint">Round 1</div></div>
<div class="toolbar" style="justify-content:center"><button class="btn" id="go" type="button" onclick="toggle()">Start</button><button class="btn ghost" type="button" onclick="reset()">Reset</button></div>
<div class="sc-two" style="margin-top:12px"><div><label for="fo">Focus (min)</label><input class="full" id="fo" type="number" min="1" max="120" value="25" inputmode="numeric" onchange="reset()"></div>
<div><label for="br">Short break (min)</label><input class="full" id="br" type="number" min="1" max="60" value="5" inputmode="numeric" onchange="reset()"></div></div>
<div class="hint">After every 4 focus rounds you get a long break of 15 minutes. Keep this tab open while the timer runs.</div>""") + _script(r"""
var mode="f",round=1,left=0,timer=null,end=0;
function cfg(){var f=Math.max(1,num("fo")||25),b=Math.max(1,num("br")||5);return {f:f*60,b:b*60,l:900};}
function fmt(s){var m=Math.floor(s/60),x=s%60;return (m<10?"0":"")+m+":"+(x<10?"0":"")+x;}
function show(){$("clock").textContent=fmt(left);$("mode").textContent=mode==="f"?"Focus":mode==="b"?"Short break":"Long break";$("round").textContent="Round "+round;document.title=fmt(left)+" - Nexora Pomodoro";}
function beep(){try{var c=new (window.AudioContext||window.webkitAudioContext)(),o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);g.gain.value=0.08;o.frequency.value=660;o.start();setTimeout(function(){o.stop();c.close();},400);}catch(e){}}
function next(){beep();var c=cfg();if(mode==="f"){if(round%4===0){mode="l";left=c.l;}else{mode="b";left=c.b;}}else{mode="f";round++;left=c.f;}end=Date.now()+left*1000;show();}
function tick(){left=Math.max(0,Math.round((end-Date.now())/1000));if(left<=0){next();return;}show();}
function toggle(){if(timer){clearInterval(timer);timer=null;$("go").textContent="Resume";return;}end=Date.now()+left*1000;timer=setInterval(tick,500);$("go").textContent="Pause";}
function reset(){if(timer){clearInterval(timer);timer=null;}mode="f";round=1;left=cfg().f;$("go").textContent="Start";show();}
reset();""")

MAIL_BODY = CSS + _hero("Internship Application Email Generator", "Fill a few boxes and get a short, polite internship or job application email you can copy. Nothing is sent or stored.") + _wrap("""
<div class="sc-two"><div><label for="nm">Your name</label><input class="full" id="nm" placeholder="Your full name"></div>
<div><label for="ro">Role you want</label><input class="full" id="ro" placeholder="e.g. Data Analyst Intern"></div></div>
<div class="sc-two"><div><label for="co">Company</label><input class="full" id="co" placeholder="Company name"></div>
<div><label for="hr">Recipient name (optional)</label><input class="full" id="hr" placeholder="e.g. Ms Rao"></div></div>
<label for="cl">College and course</label><input class="full" id="cl" placeholder="e.g. 3rd year B.E. Computer Science, ABC College">
<label for="sk">Top skills (comma separated)</label><input class="full" id="sk" placeholder="e.g. Python, Excel, communication">
<label for="pj">One project or achievement (optional)</label><input class="full" id="pj" placeholder="e.g. built an attendance tracker for my class">
<div class="toolbar"><button class="btn" type="button" onclick="run()">Write email</button></div>""") + _script(r"""
function run(){err("");var nm=$("nm").value.trim(),ro=$("ro").value.trim(),co=$("co").value.trim(),hr=$("hr").value.trim(),cl=$("cl").value.trim(),sk=$("sk").value.trim(),pj=$("pj").value.trim();
 if(!nm||!ro||!co||!cl){err("Fill your name, role, company and college.");return;}
 var skl=sk?sk.split(",").map(function(x){return x.trim();}).filter(Boolean):[],skt=skl.length?skl.slice(0,-1).join(", ")+(skl.length>1?" and ":"")+skl[skl.length-1]:"";
 var t="Subject: Application for "+ro+" - "+nm+"\n\nDear "+(hr?hr:"Hiring Team")+",\n\nI am "+nm+", "+cl+". I am writing to apply for the "+ro+" position at "+co+".\n\n"+
 (skt?"I have worked on "+skt+" during my studies and I want to use these skills on real work. ":"")+(pj?"Recently, "+pj+". ":"")+"I learn fast, I finish what I start, and I am ready to put in the effort this role needs.\n\nI have attached my resume. I would be glad to talk about how I can help your team, at a time that suits you.\n\nThank you for your time.\n\nRegards,\n"+nm;
 out('<div class="sc-res"><textarea id="mailtxt" rows="14" style="width:100%;box-sizing:border-box;padding:12px;border:1px solid #d9d6ee;border-radius:10px;font-size:15px;font-family:inherit">'+esc(t)+'</textarea><div class="toolbar"><button class="btn ghost" type="button" onclick="cp()">Copy email</button><span id="cpm" class="hint"></span></div><div class="hint">Add the resume as an attachment before you send. Read it once and change anything that does not sound like you.</div></div>');}
function cp(){var e=$("mailtxt");e.select();try{document.execCommand("copy");$("cpm").textContent="Copied";}catch(x){$("cpm").textContent="Press Ctrl+C to copy";}}""")

RESUME_BODY = CSS + _hero("Fresher Resume Guide for Students", "What to put on a first resume, in what order, and the mistakes that get resumes rejected. Then build yours in Nexora.") + """
<section class="section"><div class="container" style="max-width:780px"><div class="card">
<h2 style="margin-top:0">Resume order for freshers</h2>
<ol style="line-height:1.8"><li><b>Name and contact</b>: name, phone, a professional email, city. Add a LinkedIn or GitHub link if it is tidy.</li>
<li><b>Career objective</b>: two lines. Say the role you want and your strongest skill.</li>
<li><b>Education</b>: degree, college, year, CGPA or percentage. Put the latest first.</li>
<li><b>Projects</b>: two or three. For each, write what you built, the tools you used and the result.</li>
<li><b>Skills</b>: only skills you can talk about in an interview.</li>
<li><b>Internships, certificates, achievements</b>: short bullets with numbers where you can.</li>
<li><b>Extra activities</b>: clubs, volunteering, sports, if space allows.</li></ol>
<h2>Mistakes to avoid</h2>
<ul style="line-height:1.8"><li>A resume longer than one page.</li><li>Photos, colourful designs and tables that job filters (ATS) cannot read.</li><li>Skill bars such as "Excel 80%". List the skill and show it in a project.</li><li>Spelling mistakes and an email like cooldude123@.</li><li>Sending the same resume for every role. Copy words from the job description that are true for you.</li></ul>
<h2>Check before you send</h2>
<ul style="line-height:1.8"><li>Save as PDF with your name in the file name.</li><li>Read it on your phone. Is it clear in 10 seconds?</li><li>Ask a friend to find one mistake.</li></ul>
<div class="toolbar"><a class="btn" href="/resume-builder">Build my resume</a><a class="btn ghost" href="/career/ats-optimizer">Check ATS fit</a><a class="btn ghost" href="/students/internship-email-generator">Write application email</a></div>
</div></div></section>"""


WORDS_BODY = CSS + _hero("Word Counter and Reading Time", "Paste your essay, assignment or answer. Get words, characters, sentences, paragraphs and reading time. Your text stays in your browser.") + _wrap("""
<textarea id="wt" rows="10" style="width:100%;box-sizing:border-box;padding:12px;border:1px solid #d9d6ee;border-radius:10px;font-size:16px;font-family:inherit" placeholder="Paste or type your text here" oninput="run()"></textarea>
<div id="hub_out"></div>
<div class="hint">Reading time uses 200 words a minute and speaking time uses 130 words a minute. These are common averages.</div>""".replace('<div id="hub_out"></div>\n','')) + _script(r"""
function run(){var t=$("wt").value,s=hubWords(t);
 out('<div class="sc-res"><b class="big">'+s.words+' words</b><table><tr><td>Characters (with spaces)</td><td>'+s.chars+'</td></tr><tr><td>Characters (no spaces)</td><td>'+s.nospace+'</td></tr><tr><td>Sentences</td><td>'+s.sentences+'</td></tr><tr><td>Paragraphs</td><td>'+s.paras+'</td></tr><tr><td>Reading time</td><td>'+r2(s.words/200).toFixed(1)+' min</td></tr><tr><td>Speaking time</td><td>'+r2(s.words/130).toFixed(1)+' min</td></tr></table></div>');}
run();""")

TIME_BODY = CSS + """<style>@media print{.topnav,footer,.page-hero,.sc-noprint,.err{display:none!important}.card{box-shadow:none!important;border:0!important}}
.tt{width:100%;border-collapse:collapse;min-width:620px}.tt th,.tt td{border:1px solid #d9d6ee;padding:4px}.tt th{background:#f3efff;font-size:14px}
.tt input{width:100%;border:0;padding:8px 4px;font-size:15px;background:transparent;box-sizing:border-box;text-align:center}.ttw{overflow-x:auto}</style>""" + _hero("Weekly Timetable Maker", "Type your classes or study slots into the grid. It saves on this device and prints cleanly on one page.") + _wrap("""
<div class="ttw"><table class="tt" id="tt"></table></div>
<div class="toolbar sc-noprint"><button class="btn ghost" type="button" onclick="addPeriod()">+ Add period</button><button class="btn ghost" type="button" onclick="delPeriod()">Remove last period</button><button class="btn" type="button" onclick="window.print()">Print / Save as PDF</button><button class="btn ghost" type="button" onclick="clearAll()">Clear all</button></div>
<div class="hint sc-noprint">Saved only in this browser. In the print window choose "Save as PDF" to keep a copy. The time labels in the first column are editable.</div>""") + _script(r"""
var KEY="nexora_timetable_v1",DAYS=["Mon","Tue","Wed","Thu","Fri","Sat"];
var data=(function(){try{var d=JSON.parse(localStorage.getItem(KEY));if(d&&d.t&&d.c)return d;}catch(e){}return {t:["9:00","10:00","11:00","12:00","2:00","3:00"],c:{}};})();
function save(){try{localStorage.setItem(KEY,JSON.stringify(data));}catch(e){}}
function draw(){var h="<tr><th>Time</th>"+DAYS.map(function(d){return "<th>"+d+"</th>";}).join("")+"</tr>";
 data.t.forEach(function(t,i){h+='<tr><td><input value="'+esc(t)+'" data-t="'+i+'" aria-label="Time"></td>';
  DAYS.forEach(function(d,j){h+='<td><input value="'+esc(data.c[i+"_"+j]||"")+'" data-c="'+i+"_"+j+'" aria-label="'+d+' period '+(i+1)+'"></td>';});h+="</tr>";});
 $("tt").innerHTML=h;}
document.addEventListener("input",function(e){var x=e.target;if(x.dataset&&x.dataset.t!==undefined){data.t[x.dataset.t]=x.value;save();}else if(x.dataset&&x.dataset.c){data.c[x.dataset.c]=x.value;save();}});
function addPeriod(){data.t.push("");save();draw();}
function delPeriod(){if(data.t.length<=1)return;var i=data.t.length-1;data.t.pop();DAYS.forEach(function(d,j){delete data.c[i+"_"+j];});save();draw();}
function clearAll(){if(!confirm("Clear the whole timetable?"))return;data.c={};save();draw();}
draw();""")

PHOTO_BODY = CSS + _hero("Photo and Signature Resizer for Forms", "Resize a photo or signature to the pixel size and KB limit your admission, exam or job form asks for. It all happens in your browser. Nothing is uploaded.") + _wrap("""
<label for="pf">Choose photo or signature</label><input class="full" id="pf" type="file" accept="image/*">
<div class="sc-two"><div><label for="pw">Width (px)</label><input class="full" id="pw" type="number" min="20" max="4000" value="413" inputmode="numeric"></div>
<div><label for="ph">Height (px)</label><input class="full" id="ph" type="number" min="20" max="4000" value="531" inputmode="numeric"></div></div>
<div class="sc-two"><div><label for="pk">Maximum size (KB)</label><input class="full" id="pk" type="number" min="5" max="5000" value="50" inputmode="numeric"></div>
<div><label for="pp">Size preset</label><select class="full" id="pp" onchange="preset()"><option value="">Custom</option><option value="413,531">3.5 x 4.5 cm photo (300 dpi, 413 x 531)</option><option value="300,300">Square 300 x 300</option><option value="200,230">200 x 230 photo</option><option value="140,60">Signature 140 x 60</option></select></div></div>
<label for="pm">Fit</label><select class="full" id="pm"><option value="cover">Fill the size (crop the edges)</option><option value="contain">Keep whole image (white margins)</option></select>
<div class="toolbar"><button class="btn" type="button" onclick="run()">Resize</button></div>
<div class="hint">Check your form's instructions for the exact pixel size, KB range and format. Output is JPEG. Presets are common sizes only, not tied to any one exam. The 3.5 x 4.5 cm preset is computed as cm to inches times 300 dpi.</div>""") + _script(r"""
function preset(){var v=$("pp").value;if(!v)return;var p=v.split(",");$("pw").value=p[0];$("ph").value=p[1];}
function draw(img,w,h,mode){var c=document.createElement("canvas");c.width=w;c.height=h;var x=c.getContext("2d");x.fillStyle="#fff";x.fillRect(0,0,w,h);
 var sw=img.naturalWidth,sh=img.naturalHeight,k=mode==="cover"?Math.max(w/sw,h/sh):Math.min(w/sw,h/sh),dw=sw*k,dh=sh*k;x.drawImage(img,(w-dw)/2,(h-dh)/2,dw,dh);return c;}
function blobAt(c,q){return new Promise(function(r){c.toBlob(r,"image/jpeg",q);});}
async function fit(img,w,h,mode,maxB){var c=draw(img,w,h,mode),lo=0.05,hi=0.95,best=null;
 var b=await blobAt(c,hi);if(b.size<=maxB)return b;
 for(var i=0;i<8;i++){var m=(lo+hi)/2,t=await blobAt(c,m);if(t.size<=maxB){best=t;lo=m;}else hi=m;}
 return best;}
async function run(){err("");var f=$("pf").files[0],w=num("pw"),h=num("ph"),kb=num("pk");
 if(!f){err("Choose an image first.");return;}if(isNaN(w)||isNaN(h)||isNaN(kb)||w<20||h<20||kb<5){err("Check width, height and maximum KB.");return;}
 var url=URL.createObjectURL(f),img=new Image();
 img.onload=async function(){var b=await fit(img,w,h,$("pm").value,kb*1024);URL.revokeObjectURL(url);
  if(!b){err("Could not get under "+kb+" KB at "+w+" x "+h+". Try a larger KB limit or a smaller pixel size.");return;}
  var u=URL.createObjectURL(b);
  out('<div class="sc-res"><b class="big">'+r2(b.size/1024).toFixed(1)+' KB</b><div>'+w+' x '+h+' px, JPEG (limit '+kb+' KB)</div><div style="margin:12px 0"><img src="'+u+'" alt="Resized preview" style="max-width:100%;max-height:320px;border:1px solid #d9d6ee;border-radius:8px"></div><a class="btn" download="nexora-resized.jpg" href="'+u+'">Download JPEG</a></div>');};
 img.onerror=function(){err("That file could not be read as an image.");};img.src=url;}""")

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
    "exam-countdown": dict(
        name="Exam Countdown", icon="D", short="Days and hours left for each exam, saved on your device.",
        title="Exam Countdown Timer - Days Left for Your Exams | Nexora",
        meta="Free exam countdown timer for students. Add your exams and see the days, hours and minutes left. Saved on your device, no sign-up.",
        body=COUNT_BODY,
        faq=[["Where is my exam list saved?", "In your own browser on this device. It is never uploaded, so it will not show on another phone or computer."],
             ["Why does it show Started or over?", "The date and time you set has passed. Remove it or add the next exam."]]),
    "study-planner": dict(
        name="Study Planner", icon="S", short="Split your study hours across subjects before the exam.",
        title="Study Planner - Hours per Subject Before Exam | Nexora",
        meta="Free study planner for students. Enter exam date, daily study hours and subjects. Get hours per day and total hours for each subject.",
        body=PLAN_BODY,
        faq=[["How does the planner split the time?", "It multiplies your study days by your daily hours, then shares that time across subjects in proportion to the difficulty you give each one."],
             ["Why keep revision days?", "A day or two at the end for revision and past papers helps you remember more than learning new topics at the last minute."]]),
    "pomodoro-timer": dict(
        name="Pomodoro Timer", icon="P", short="25 minute focus blocks with breaks and a soft beep.",
        title="Pomodoro Study Timer - 25 Minute Focus Timer | Nexora",
        meta="Free Pomodoro timer for studying. 25 minute focus rounds, 5 minute breaks and a long break after four rounds. Works on your phone.",
        body=POMO_BODY,
        faq=[["What is the Pomodoro method?", "You study with full focus for 25 minutes, rest for 5, and take a longer break after four rounds."],
             ["Can I change the times?", "Yes. Change the focus and break boxes. The timer resets with your new values."]]),
    "internship-email-generator": dict(
        name="Internship Email Writer", icon="@", short="Write a clear internship or job application email in a minute.",
        title="Internship Application Email Generator - Free | Nexora",
        meta="Free internship and job application email writer for freshers. Fill your details and copy a polite, short email. Nothing is stored.",
        body=MAIL_BODY,
        faq=[["Should I attach my resume?", "Yes. Attach it as a PDF with your name in the file name, and mention it in the email."],
             ["Can I edit the email?", "Yes. Edit the text in the box before you copy it so it sounds like you."]]),
    "fresher-resume-guide": dict(
        name="Fresher Resume Guide", icon="R", short="What to put on your first resume and what to skip.",
        title="Fresher Resume Guide - Format, Order and Mistakes | Nexora",
        meta="Simple guide to writing a fresher resume: section order, what to include, mistakes to avoid and a checklist. Then build yours free to preview.",
        body=RESUME_BODY,
        faq=[["How long should a fresher resume be?", "One page. Recruiters scan quickly, so keep only what supports the role."],
             ["Do I need work experience?", "No. Projects, internships, certificates and activities show what you can do."]]),
    "word-counter": dict(
        name="Word Counter", icon="W", short="Words, characters, sentences and reading time.",
        title="Word Counter - Words, Characters and Reading Time | Nexora",
        meta="Free word counter for essays and assignments. Count words, characters, sentences and paragraphs, with reading and speaking time. Private, in your browser.",
        body=WORDS_BODY,
        faq=[["How are words counted?", "Any group of characters separated by spaces or line breaks counts as one word."],
             ["Is my text saved?", "No. The counting happens in your browser and the text is never sent anywhere."]]),
    "timetable-maker": dict(
        name="Timetable Maker", icon="T", short="Weekly class or study timetable you can print.",
        title="Weekly Timetable Maker - Free Printable Class Timetable | Nexora",
        meta="Free weekly timetable maker for students. Fill a Monday to Saturday grid, add periods, save it on your device and print or save as PDF.",
        body=TIME_BODY,
        faq=[["Can I print my timetable?", "Yes. Press Print / Save as PDF. The menu and buttons are hidden in the printout."],
             ["Where is it saved?", "In this browser on this device only. Print or save a PDF if you want a copy elsewhere."]]),
    "photo-signature-resizer": dict(
        name="Photo and Signature Resizer", icon="KB", short="Resize to exact pixels and a KB limit for forms.",
        title="Photo and Signature Resizer - Reduce KB for Forms | Nexora",
        meta="Free photo and signature resizer for admission, exam and job forms. Set width, height and maximum KB. Works in your browser, nothing is uploaded.",
        body=PHOTO_BODY,
        faq=[["Is my photo uploaded?", "No. The image is resized in your browser and never leaves your device."],
             ["What if my form wants a different format or a minimum size?", "This tool outputs JPEG under your maximum KB. If your form also asks for a minimum size or another format, read its instructions and adjust the size boxes."]]),
    "cgpa-percentage-converter": dict(
        name="CGPA / Percentage Converter", icon="CG", short="Convert CGPA to percentage and back, four formulas.",
        title="CGPA to Percentage and Percentage to CGPA Converter | Nexora",
        meta="Free converter for CGPA to percentage and percentage to CGPA. Choose the (CGPA-0.75)x10, (CGPA-0.5)x10, CGPAx10 or CGPAx9.5 formula.",
        body=CONVERT_BODY,
        faq=[["Which CGPA to percentage formula should I use?", "Use the one your university states. VTU publishes (CGPA - 0.75) x 10 for some schemes, and CBSE uses CGPA x 9.5 for its 10-point grades. When unsure, ask your university office."],
             ["Is the result official?", "No. It is an estimate for forms and planning."]]),
}

# Tools in the hub, grouped. Entries are (href, title, description).
def _t(slug):
    v = TOOLS[slug]
    return ("/students/" + slug, v["name"], v["short"])


LINK_GROUPS = [
    ("Marks, grades and attendance", [_t(k) for k in ("percentage-calculator", "attendance-calculator", "final-marks-needed-calculator", "gpa-calculator", "cgpa-percentage-converter")] + [
        ("/vtu-sgpa-calculator", "VTU SGPA Calculator", "Semester SGPA from credits and grades."),
        ("/vtu-cgpa-calculator", "VTU CGPA Calculator", "CGPA across semesters, lateral entry too."),
        ("/cgpa-to-percentage-calculator", "CGPA to Percentage (VTU)", "VTU formula with a simple option.")]),
    ("Plan and focus", [_t(k) for k in ("exam-countdown", "study-planner", "timetable-maker", "pomodoro-timer", "word-counter")]),
    ("PDF and form tools", [_t("photo-signature-resizer"),
        ("/pdf/merge", "Merge PDF", "Join notes and assignments into one file."),
        ("/pdf/compress", "Compress PDF", "Shrink a PDF to fit upload limits."),
        ("/pdf/jpg-to-pdf", "JPG to PDF", "Turn photos of handwritten pages into a PDF."),
        ("/pdf/scan-to-pdf", "Scan to PDF", "Make a clean PDF from phone photos."),
        ("/pdf/word-to-pdf", "Word to PDF", "Convert a report before you submit it."),
        ("/pdf/split", "Split PDF", "Pull out the pages you need.")]),
    ("Resume, internships and jobs", [_t("fresher-resume-guide"), _t("internship-email-generator"),
        ("/resume-builder", "Resume Builder", "Build a fresher resume (Rs 99 per CV)."),
        ("/career/ats-optimizer", "ATS Resume Checker", "See if your resume passes job filters."),
        ("/career/cover-letter-builder", "Cover Letter Writer", "Write a cover letter for an internship or job.")]),
]


def home_strip():
    return ('<section class="section" style="padding-bottom:0"><div class="container"><div style="background:#fff;border:1px solid #e6e1f7;border-radius:20px;padding:20px 24px;display:flex;flex-wrap:wrap;align-items:center;gap:14px;justify-content:space-between">'
            '<div style="flex:1 1 300px"><h2 style="margin:0 0 4px;font-size:22px">For students</h2>'
            '<p style="margin:0;color:#6b7280">CGPA, percentage and attendance calculators, study planner, PDF tools and a fresher resume. All free.</p></div>'
            '<a class="btn" href="/students">Open student tools</a></div></div></section>')


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
