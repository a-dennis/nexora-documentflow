"""Nexora student calculators: SGPA, CGPA and CGPA-to-percentage (VTU style).

Pure formulas live in the JS block below (run in the browser, nothing is
stored). The same formulas are mirrored in Python for the test cases.
"""

GRADE_POINTS = {"S": 10, "A": 9, "B": 8, "C": 7, "D": 6, "E": 4, "F": 0}


def sgpa(rows):
    """rows = [(credits, grade_point)] -> (total_credits, credit_points, sgpa)"""
    tc = sum(c for c, _ in rows)
    cp = sum(c * g for c, g in rows)
    return tc, cp, (cp / tc if tc else None)


def cgpa(sems):
    """sems = [(credits, sgpa)] -> (total_credits, weighted_points, cgpa)"""
    tc = sum(c for c, _ in sems)
    wp = sum(c * s for c, s in sems)
    return tc, wp, (wp / tc if tc else None)


def percentage(cg, method="vtu"):
    return (cg - 0.75) * 10 if method == "vtu" else cg * 10


JS = r"""
<script>
var GP = {S: 10, A: 9, B: 8, C: 7, D: 6, E: 4, F: 0};
function r2(x) { return Math.round(x * 100) / 100; }
function calcSgpa(rows) {
  var tc = 0, cp = 0;
  rows.forEach(function (r) { tc += r[0]; cp += r[0] * r[1]; });
  return {credits: tc, points: cp, sgpa: tc > 0 ? cp / tc : null};
}
function calcCgpa(sems) {
  var tc = 0, wp = 0;
  sems.forEach(function (s) { tc += s[0]; wp += s[0] * s[1]; });
  return {credits: tc, points: wp, cgpa: tc > 0 ? wp / tc : null};
}
function calcPct(cg, method) { return method === "vtu" ? (cg - 0.75) * 10 : cg * 10; }
function $(id) { return document.getElementById(id); }
function showErr(m) { $("sc_err").textContent = m || ""; }
function row(h) { return '<div class="sc-row">' + h + '</div>'; }
function gradeSelect() {
  var o = '<option value="">Grade</option>';
  Object.keys(GP).forEach(function (g) { o += '<option value="' + GP[g] + '">' + g + ' (' + GP[g] + ')</option>'; });
  return '<select class="sc-g">' + o + '</select>';
}
function removeRow(btn) { btn.parentNode.remove(); }
</script>
"""

CSS = """<style>
.sc-row{display:flex;gap:8px;margin-bottom:10px;align-items:center;flex-wrap:wrap}
.sc-row input,.sc-row select,.sc-box input,.sc-box select{padding:11px 12px;border:1px solid #d9d6ee;border-radius:10px;font-size:16px;min-width:0;max-width:100%;background:#fff}
.sc-row input.sc-n{flex:2 1 120px}.sc-row input.sc-c,.sc-row input.sc-s{flex:1 1 80px}.sc-row select{flex:1 1 110px}
.sc-x{border:0;background:#f3f1fb;border-radius:10px;padding:10px 12px;cursor:pointer;font-size:16px}
.sc-res{margin-top:16px;padding:16px;border-radius:14px;background:linear-gradient(135deg,#f3efff,#ffeef7)}
.sc-res b.big{font-size:2rem;display:block}
.sc-res table{width:100%;border-collapse:collapse;margin-top:8px}.sc-res td{padding:6px 0;border-top:1px solid #e6e1f7}
.sc-box label{display:block;margin:10px 0 4px;font-weight:600}
@media(max-width:560px){.sc-row input.sc-n{flex:1 1 100%}}
</style>"""

SGPA_BODY = CSS + """
<section class="page-hero"><div class="container">
  <span class="tag live">Free student tool</span>
  <h1 style="margin-top:12px">SGPA Calculator (VTU 10-point scale)</h1>
  <p>Add each subject with its credits and grade. Get your semester SGPA and approximate percentage instantly. Nothing is stored - it all runs in your browser.</p>
</div></section>
<section class="section"><div class="container" style="max-width:780px"><div class="card sc-box">
  <div id="rows"></div>
  <div class="toolbar"><button class="btn ghost" type="button" onclick="addRow()">+ Add subject</button>
  <button class="btn" type="button" onclick="runSgpa()">Calculate SGPA</button></div>
  <div class="err" id="sc_err"></div>
  <div id="sc_out"></div>
  <div class="hint">Grade scale used: S=10, A=9, B=8, C=7, D=6, E=4, F=0 (as in the VTU regulations text). Check the scale printed on your own marks card - schemes differ.</div>
</div></section>
""" + JS + """
<script>
function addRow() {
  var d = document.createElement("div"); d.className = "sc-row";
  d.innerHTML = '<input class="sc-n" placeholder="Subject (optional)">' +
    '<input class="sc-c" type="number" min="0" step="0.5" inputmode="decimal" placeholder="Credits">' +
    gradeSelect() + '<button type="button" class="sc-x" onclick="removeRow(this)" aria-label="Remove">x</button>';
  $("rows").appendChild(d);
}
function runSgpa() {
  showErr(""); var rows = [], bad = false;
  document.querySelectorAll("#rows .sc-row").forEach(function (r) {
    var c = r.querySelector(".sc-c").value, g = r.querySelector(".sc-g").value;
    if (c === "" && g === "") return;
    if (c === "" || g === "" || Number(c) < 0) { bad = true; return; }
    rows.push([Number(c), Number(g)]);
  });
  if (bad) { showErr("Each subject needs credits and a grade."); return; }
  var s = calcSgpa(rows);
  if (!s.sgpa && s.sgpa !== 0) { showErr("Add at least one subject with credits."); return; }
  $("sc_out").innerHTML = '<div class="sc-res"><b class="big">SGPA ' + r2(s.sgpa).toFixed(2) + '</b>' +
    '<table><tr><td>Total credits</td><td>' + s.credits + '</td></tr><tr><td>Total credit points</td><td>' + s.points + '</td></tr>' +
    '<tr><td>Formula</td><td>' + s.points + ' / ' + s.credits + '</td></tr>' +
    '<tr><td>Approx. percentage (SGPA - 0.75) x 10</td><td>' + r2(calcPct(s.sgpa, "vtu")).toFixed(2) + '%</td></tr></table></div>';
}
for (var i = 0; i < 6; i++) addRow();
</script>
"""

CGPA_BODY = CSS + """
<section class="page-hero"><div class="container">
  <span class="tag live">Free student tool</span>
  <h1 style="margin-top:12px">CGPA Calculator (semester-wise, VTU style)</h1>
  <p>Enter the credits and SGPA of each semester to get your overall CGPA and percentage. Lateral entry students can skip semesters 1 and 2.</p>
</div></section>
<section class="section"><div class="container" style="max-width:780px"><div class="card sc-box">
  <label style="display:flex;gap:8px;align-items:center;margin-top:0"><input type="checkbox" id="lat" onchange="buildSems()" style="width:auto"> Lateral entry (diploma) - start from semester 3</label>
  <div id="rows" style="margin-top:12px"></div>
  <label>Percentage method</label>
  <select id="meth"><option value="vtu">VTU formula: (CGPA - 0.75) x 10</option><option value="x10">Simple: CGPA x 10</option></select>
  <div class="toolbar"><button class="btn" type="button" onclick="runCgpa()">Calculate CGPA</button></div>
  <div class="err" id="sc_err"></div>
  <div id="sc_out"></div>
  <div class="hint">CGPA = sum of (semester credits x SGPA) / sum of semester credits. Leave a semester empty to skip it. The (CGPA - 0.75) x 10 formula is the one published by VTU for the 2015, 2017 and 2018 schemes; check your university circular for later schemes.</div>
</div></section>
""" + JS + """
<script>
function buildSems() {
  var start = $("lat").checked ? 3 : 1, h = "";
  for (var i = start; i <= 8; i++) {
    h += row('<span style="min-width:90px;font-weight:600">Semester ' + i + '</span>' +
      '<input class="sc-c" type="number" min="0" step="0.5" inputmode="decimal" placeholder="Credits" value="' + (i < 7 ? 20 : (i == 7 ? 24 : 16)) + '">' +
      '<input class="sc-s" type="number" min="0" max="10" step="0.01" inputmode="decimal" placeholder="SGPA">');
  }
  $("rows").innerHTML = h;
}
function runCgpa() {
  showErr(""); var sems = [], bad = false;
  document.querySelectorAll("#rows .sc-row").forEach(function (r) {
    var c = r.querySelector(".sc-c").value, s = r.querySelector(".sc-s").value;
    if (s === "") return;
    if (c === "" || Number(c) <= 0 || Number(s) < 0 || Number(s) > 10) { bad = true; return; }
    sems.push([Number(c), Number(s)]);
  });
  if (bad) { showErr("Credits must be above 0 and SGPA between 0 and 10."); return; }
  var g = calcCgpa(sems);
  if (g.cgpa === null) { showErr("Enter the SGPA of at least one semester."); return; }
  var m = $("meth").value;
  $("sc_out").innerHTML = '<div class="sc-res"><b class="big">CGPA ' + r2(g.cgpa).toFixed(2) + '</b><table>' +
    '<tr><td>Semesters counted</td><td>' + sems.length + '</td></tr><tr><td>Total credits</td><td>' + g.credits + '</td></tr>' +
    '<tr><td>Percentage</td><td>' + r2(calcPct(g.cgpa, m)).toFixed(2) + '%</td></tr></table></div>';
}
buildSems();
</script>
"""

PCT_BODY = CSS + """
<section class="page-hero"><div class="container">
  <span class="tag live">Free student tool</span>
  <h1 style="margin-top:12px">CGPA to Percentage Calculator</h1>
  <p>Convert your CGPA or SGPA to a percentage, or a percentage back to CGPA, in one tap.</p>
</div></section>
<section class="section"><div class="container" style="max-width:780px"><div class="card sc-box">
  <label>Convert</label>
  <select id="dir"><option value="c2p">CGPA to percentage</option><option value="p2c">Percentage to CGPA</option></select>
  <label>Value</label>
  <input id="val" type="number" step="0.01" inputmode="decimal" placeholder="e.g. 8.5 or 78" style="width:100%">
  <label>Method</label>
  <select id="meth"><option value="vtu">VTU formula: (CGPA - 0.75) x 10</option><option value="x10">Simple: CGPA x 10</option></select>
  <div class="toolbar"><button class="btn" type="button" onclick="runPct()">Convert</button></div>
  <div class="err" id="sc_err"></div>
  <div id="sc_out"></div>
  <div class="hint">The (CGPA - 0.75) x 10 formula is published by VTU for the 2015, 2017 and 2018 schemes. For other universities or schemes, use the formula in your own university rules.</div>
</div></section>
""" + JS + """
<script>
function runPct() {
  showErr(""); var v = parseFloat($("val").value), m = $("meth").value, d = $("dir").value;
  if (isNaN(v) || v < 0) { showErr("Enter a valid number."); return; }
  var out;
  if (d === "c2p") {
    if (v > 10) { showErr("CGPA cannot be above 10."); return; }
    out = "Percentage " + r2(calcPct(v, m)).toFixed(2) + "%";
  } else {
    if (v > 100) { showErr("Percentage cannot be above 100."); return; }
    out = "CGPA " + r2(m === "vtu" ? v / 10 + 0.75 : v / 10).toFixed(2);
  }
  $("sc_out").innerHTML = '<div class="sc-res"><b class="big">' + out + '</b></div>';
}
</script>
"""

PAGES = {
    "vtu-sgpa-calculator": {
        "title": "VTU SGPA Calculator - Free Semester SGPA Calculator | Nexora",
        "meta": "Free SGPA calculator for VTU and other 10-point grading systems. Add subjects, credits and grades to get your semester SGPA and approximate percentage.",
        "body": SGPA_BODY,
        "faq": [["How is SGPA calculated?", "SGPA = sum of (credits x grade points) divided by the total credits of the semester."],
                ["Do I need to enter credits?", "Yes. Credits are printed in your syllabus or marks card; enter the credit value for each subject."]],
    },
    "vtu-cgpa-calculator": {
        "title": "VTU CGPA Calculator - Free CGPA & Percentage Calculator | Nexora",
        "meta": "Free CGPA calculator for VTU students. Enter semester credits and SGPA to get your CGPA and percentage. Lateral entry option included.",
        "body": CGPA_BODY,
        "faq": [["How is CGPA calculated?", "CGPA = sum of (semester credits x semester SGPA) divided by the sum of semester credits."],
                ["What about lateral entry?", "Lateral entry students join in the third semester, so tick the lateral entry box and only semesters 3 to 8 are counted."]],
    },
    "cgpa-to-percentage-calculator": {
        "title": "CGPA to Percentage Calculator - VTU Formula | Nexora",
        "meta": "Convert CGPA to percentage and percentage to CGPA free. Uses the VTU formula (CGPA - 0.75) x 10 or a simple CGPA x 10 option.",
        "body": PCT_BODY,
        "faq": [["What is the VTU CGPA to percentage formula?", "VTU publishes Percentage = (CGPA - 0.75) x 10 for the 2015, 2017 and 2018 schemes."],
                ["Is this an official conversion?", "No. It is an estimate. Your university or employer may use a different rule, so confirm with them when it matters."]],
    },
}

CARDS = [("/vtu-sgpa-calculator", "SGPA Calculator", "Semester SGPA from credits and grades."),
         ("/vtu-cgpa-calculator", "CGPA Calculator", "Overall CGPA across semesters, lateral entry too."),
         ("/cgpa-to-percentage-calculator", "CGPA to Percentage", "Convert CGPA to percentage and back.")]


def links_block() -> str:
    return ('<section class="section" style="padding-top:0"><div class="container" style="max-width:780px"><div class="card">'
            '<h2 style="margin-top:0">Student calculators</h2><div style="display:flex;flex-wrap:wrap;gap:10px">'
            + "".join(f'<a class="btn ghost" href="{h}">{n}</a>' for h, n, _ in CARDS)
            + '</div></div></div></section>')


def render(slug: str, page_fn) -> str:
    spec = PAGES[slug]
    faqs = "".join(f"<h3 style='margin:18px 0 6px'>{q}</h3><p>{a}</p>" for q, a in spec["faq"])
    more = "".join(f'<a class="btn ghost" href="{h}">{n}</a>' for h, n, _ in CARDS if h != "/" + slug)
    extra = ('<section class="section" style="padding-top:0"><div class="container" style="max-width:780px">'
             f'<div class="card"><h2 style="margin-top:0">Common questions</h2>{faqs}</div>'
             f'<div class="card"><h2 style="margin-top:0">More free Nexora tools</h2><div style="display:flex;flex-wrap:wrap;gap:10px">{more}'
             '<a class="btn ghost" href="/hr/calculators">HR calculators</a></div></div></div></section>')
    return page_fn(spec["title"], spec["meta"], "", spec["body"] + extra)
