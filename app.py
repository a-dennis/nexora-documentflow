import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

APP_NAME = "NEXORA"
MODEL = "gemini-3.5-flash-lite"
MAX_PDF_SIZE = 50 * 1024 * 1024
MAX_IMAGE_SIZE = 20 * 1024 * 1024
MAX_AI_FILE_SIZE = 20 * 1024 * 1024

st.set_page_config(page_title="Nexora — AI Document Workspace", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# NEXORA VISUAL SYSTEM — native Streamlit UI, no visible HTML
# ============================================================
st.markdown(r"""
<style>
:root{--blue:#2563eb;--indigo:#4f46e5;--violet:#7c3aed;--cyan:#0891b2;--green:#16a34a;--orange:#f97316;--pink:#ec4899;--ink:#252637;--muted:#687083}
.stApp{background:radial-gradient(circle at 4% 0%,rgba(59,130,246,.23),transparent 24%),radial-gradient(circle at 96% 1%,rgba(236,72,153,.18),transparent 24%),radial-gradient(circle at 82% 42%,rgba(124,58,237,.13),transparent 27%),radial-gradient(circle at 15% 88%,rgba(6,182,212,.14),transparent 28%),linear-gradient(135deg,#f1f8ff 0%,#fbf4ff 46%,#eefbff 100%);min-height:100vh}
.block-container{max-width:1500px!important;padding-top:.15rem!important;padding-bottom:.6rem!important;padding-left:1.1rem!important;padding-right:1.1rem!important}
[data-testid="stHeader"]{background:transparent!important;height:0!important}[data-testid="stToolbar"]{visibility:hidden;height:0}
[data-testid="stVerticalBlock"]{gap:.22rem}.element-container{margin-bottom:.03rem!important}
h1,h2,h3{color:var(--ink)!important}h1{font-weight:900!important;letter-spacing:-2.4px!important}h2{font-weight:850!important;letter-spacing:-1.2px!important}h3{font-weight:800!important}
p,li{color:#51596a}hr{border-color:rgba(148,163,184,.22)!important;margin:.22rem 0 .45rem!important}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,.92)!important;border:1px solid rgba(148,163,184,.24)!important;border-radius:18px!important;box-shadow:0 8px 28px rgba(37,52,90,.055),inset 0 1px 0 rgba(255,255,255,.96);transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
[data-testid="stVerticalBlockBorderWrapper"]:hover{border-color:rgba(79,70,229,.28)!important;box-shadow:0 14px 36px rgba(79,70,229,.12),inset 0 1px 0 rgba(255,255,255,.98)}
[data-testid="stFileUploader"]{background:linear-gradient(135deg,rgba(239,246,255,.98),rgba(250,245,255,.98))!important;border:2px dashed rgba(79,70,229,.36)!important;border-radius:18px!important;padding:.5rem!important;box-shadow:0 0 0 5px rgba(79,70,229,.035),0 14px 35px rgba(79,70,229,.075);transition:all .2s ease}
[data-testid="stFileUploader"]:hover{border-color:rgba(79,70,229,.72)!important;transform:translateY(-2px);box-shadow:0 0 0 6px rgba(79,70,229,.045),0 18px 42px rgba(79,70,229,.12)}
.stButton>button,.stDownloadButton>button{min-height:40px!important;border-radius:11px!important;font-weight:750!important;border:1px solid rgba(148,163,184,.28)!important;background:rgba(255,255,255,.93)!important;box-shadow:0 4px 14px rgba(37,52,90,.045);transition:all .16s ease}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);border-color:rgba(79,70,229,.42)!important;box-shadow:0 8px 22px rgba(79,70,229,.10)}
.stButton>button[kind="primary"],.stButton>button[kind="primary"] p,.stButton>button[kind="primary"] span,.stButton>button[kind="primary"] div{color:#fff!important}.stButton>button[kind="primary"]{color:#fff!important;border:none!important;background:linear-gradient(100deg,#2563eb,#4f46e5 48%,#8b5cf6)!important;box-shadow:0 9px 25px rgba(79,70,229,.24)}
.stButton>button[kind="primary"]:hover{background:linear-gradient(100deg,#1d4ed8,#4338ca 48%,#7c3aed)!important;box-shadow:0 12px 30px rgba(79,70,229,.30)}
div[role="radiogroup"]{gap:.3rem!important;padding:.18rem!important;background:rgba(255,255,255,.72);border:1px solid rgba(148,163,184,.2);border-radius:14px;box-shadow:0 5px 20px rgba(37,52,90,.035)}
div[role="radiogroup"] label{border-radius:10px!important;padding:.3rem .78rem!important;font-weight:700!important}
[data-testid="stChatMessage"]{border-radius:14px!important;margin-bottom:.42rem!important}[data-testid="stChatInput"]{border-radius:14px!important;box-shadow:0 8px 28px rgba(79,70,229,.12)!important}
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden!important;box-shadow:0 6px 20px rgba(37,52,90,.055)}[data-testid="stAlert"]{border-radius:12px!important}
.hr-hero{padding:.2rem 0 .35rem}.hr-badge{display:inline-block;padding:.28rem .7rem;border-radius:999px;background:rgba(255,255,255,.8);border:1px solid rgba(79,70,229,.16);font-weight:800;color:#4f46e5}.hr-card-title{font-weight:850}.hr-note{font-size:.86rem;color:#687083}.stButton>button[kind="secondary"]{font-weight:700!important}@media(max-width:900px){.block-container{padding-left:.7rem!important;padding-right:.7rem!important}h1{letter-spacing:-1.8px!important}}
</style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "document_ready": False, "interaction_id": None, "document_name": None,
    "document_type": None, "document_bytes": None, "summary": None,
    "messages": [], "active_view": "Summary", "extracted_information": None,
    "extracted_line_items": None, "analysis_result": None,
    "pricing_open": False,
    "resume_analysis": None, "resume_file_bytes": None, "resume_file_name": None, "resume_file_type": None,
    "resume_target_role": "", "improved_resume_bytes": None, "improved_resume_name": None,
    "resume_fix_paid_demo": False,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = [] if isinstance(value, list) else value

@st.cache_resource
def get_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
        st.stop()
    return genai.Client(api_key=api_key)


def auth_configured():
    try:
        return "auth" in st.secrets
    except Exception:
        return False

def logged_in():
    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False

def display_name():
    try:
        name = getattr(st.user, "name", None)
        email = getattr(st.user, "email", None)
        return str(name or (str(email).split("@")[0] if email else "User"))
    except Exception:
        return "User"

# PUBLIC-FIRST EXPERIENCE:
# Login is NOT required for the free Nexora workflow.
# Google authentication remains available for the paid checkout flow.
client = get_client()


def get_mime_type(file):
    if file.type:
        return file.type
    name = file.name.lower()
    if name.endswith(".pdf"): return "application/pdf"
    if name.endswith(".png"): return "image/png"
    if name.endswith(".jpg") or name.endswith(".jpeg"): return "image/jpeg"
    return "application/octet-stream"

def validate_file(file):
    mime = get_mime_type(file)
    if mime == "application/pdf" and file.size > MAX_PDF_SIZE:
        return False, "PDF files must be 50 MB or smaller."
    if mime.startswith("image/") and file.size > MAX_IMAGE_SIZE:
        return False, "Images must be 20 MB or smaller."
    if mime != "application/pdf" and not mime.startswith("image/"):
        return False, "Please upload a PDF, PNG, JPG or JPEG."
    return True, ""

def make_document_part(file):
    return {"type": "document" if get_mime_type(file) == "application/pdf" else "image", "data": base64.b64encode(file.getvalue()).decode("utf-8"), "mime_type": get_mime_type(file)}

def money(value):
    return f"₹{value:,.0f}"


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def validate_ai_file(file):
    if file is None:
        return False, "Please upload a file."
    if file.size > MAX_AI_FILE_SIZE:
        return False, "Please keep the file below 20 MB for this first version."
    mime = file.type or ""
    if mime != "application/pdf" and not mime.startswith("image/"):
        return False, "Please upload a PDF, PNG, JPG or JPEG."
    return True, ""


def ai_text(prompt, file=None):
    """Run a short Gemini AI task, optionally with an uploaded PDF/image.

    The HR AI tools use the same Interactions API pattern as the main
    document workflow. This keeps PDF/image inputs inline and avoids the
    undefined ai_text() error that occurred in the Phase 2 build.
    """
    try:
        inputs = [{"type": "text", "text": prompt}]
        if file is not None:
            inputs.append(make_document_part(file))

        response = client.interactions.create(
            model=MODEL,
            input=inputs,
            store=False,
            generation_config={"thinking_level": "minimal"},
        )
        result = getattr(response, "output_text", "") or ""
        if not result:
            st.error("Nexora did not receive a usable AI response.")
            return ""
        return result
    except Exception as error:
        text = str(error)
        st.error("Nexora could not complete the AI analysis.")
        if "429" in text:
            st.warning("The Gemini request limit was reached. Please wait a moment and try again.")
        elif "500" in text or "503" in text:
            st.warning("Gemini is temporarily busy. Please try again.")
        elif "400" in text:
            st.warning("The uploaded file or AI request could not be processed. Please try a different PDF/image.")
        else:
            st.warning("Please try the analysis again.")
        with st.expander("Technical details"):
            st.code(text)
        return ""


def _set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def _set_cell_border(cell, color="D9E2F3", size="6"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    borders = tcPr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcPr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def _set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def _set_doc_margins(section):
    section.top_margin = Inches(0.68)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)


def _add_field(paragraph, instruction):
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = instruction
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def _style_document(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(42, 52, 72)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.12
    for name, size, color in [
        ("Title", 24, "173B6C"),
        ("Heading 1", 13.5, "173B6C"),
        ("Heading 2", 11.5, "2563A6"),
    ]:
        stl = styles[name]
        stl.font.name = "Aptos Display" if name == "Title" else "Aptos"
        stl.font.size = Pt(size)
        stl.font.bold = True
        stl.font.color.rgb = RGBColor.from_string(color)
        stl.paragraph_format.space_before = Pt(10 if name != "Title" else 0)
        stl.paragraph_format.space_after = Pt(5)
    for sec in doc.sections:
        _set_doc_margins(sec)
        footer = sec.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.text = "CONFIDENTIAL  •  For authorized HR / business use only  •  Page "
        _add_field(footer, "PAGE")
        for r in footer.runs:
            r.font.name = "Aptos"
            r.font.size = Pt(8)
            r.font.color.rgb = RGBColor(105, 116, 135)


def _add_header(doc, title, subtitle):
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(4.9)
    table.columns[1].width = Inches(1.9)
    left, right = table.rows[0].cells
    _set_cell_shading(left, "F4F8FD")
    _set_cell_shading(right, "EAF2FF")
    _set_cell_border(left, "D8E5F5", "5")
    _set_cell_border(right, "D8E5F5", "5")
    left.vertical_alignment = right.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = left.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("[COMPANY NAME]")
    r.bold = True; r.font.name = "Aptos Display"; r.font.size = Pt(16); r.font.color.rgb = RGBColor(23,59,108)
    p2 = left.add_paragraph("Human Resources / People Operations")
    p2.paragraph_format.space_after = Pt(0)
    for r in p2.runs:
        r.font.size = Pt(8.5); r.font.color.rgb = RGBColor(91,105,125)
    p3 = right.paragraphs[0]
    p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p3.add_run("HR DOCUMENT")
    r.bold = True; r.font.size = Pt(8); r.font.color.rgb = RGBColor(37,99,235)
    p4 = right.add_paragraph(subtitle)
    p4.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p4.paragraph_format.space_after = Pt(0)
    for r in p4.runs:
        r.font.size = Pt(8); r.font.color.rgb = RGBColor(91,105,125)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    title_p = doc.add_paragraph(style="Title")
    title_p.add_run(title)
    title_p.paragraph_format.space_after = Pt(2)
    accent = doc.add_paragraph()
    accent.paragraph_format.space_after = Pt(8)
    run = accent.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    run.font.size = Pt(5); run.font.color.rgb = RGBColor(37,99,235)


def _add_metadata_table(doc, rows):
    table = doc.add_table(rows=len(rows), cols=2)
    table.autofit = False
    for i, (label, value) in enumerate(rows):
        table.columns[0].width = Inches(1.55)
        table.columns[1].width = Inches(5.25)
        c1, c2 = table.rows[i].cells
        _set_cell_shading(c1, "F7F9FC")
        _set_cell_border(c1); _set_cell_border(c2)
        p = c1.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(label.upper()); r.bold=True; r.font.size=Pt(8); r.font.color.rgb=RGBColor(80,96,120)
        p = c2.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(value); r.font.size=Pt(9.5); r.font.color.rgb=RGBColor(42,52,72)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def _add_section(doc, heading, lines):
    doc.add_heading(heading, level=1)
    for line in lines:
        p = doc.add_paragraph()
        if line.startswith("• "):
            p.style = doc.styles["Normal"]
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.first_line_indent = Inches(-0.15)
        p.add_run(line)


def _add_signature(doc, signatory="[AUTHORIZED SIGNATORY]"):
    doc.add_paragraph().paragraph_format.space_after = Pt(3)
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(3.35); table.columns[1].width = Inches(3.35)
    for cell, heading in zip(table.rows[0].cells, ["For [COMPANY NAME]", "Employee / Recipient"]):
        _set_cell_border(cell, "FFFFFF", "0")
        p = cell.paragraphs[0]; p.add_run("\n\n____________________________").bold=True
        p.add_run(f"\n{heading}\n[NAME / SIGNATURE]\n[DATE]")
        for r in p.runs: r.font.size=Pt(9); r.font.color.rgb=RGBColor(70,82,103)


def docx_bytes(title, subtitle, sections, metadata=None, form=False):
    doc = Document()
    _style_document(doc)
    _add_header(doc, title, subtitle)
    if metadata:
        _add_metadata_table(doc, metadata)
    for heading, body in sections:
        _add_section(doc, heading, body)
    if form:
        table = doc.add_table(rows=1, cols=3)
        table.autofit = False
        headers = ["Area", "Response / Rating", "Comments"]
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            _set_cell_shading(cell, "173B6C"); _set_cell_border(cell, "173B6C")
            p = cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            r=p.add_run(h); r.bold=True; r.font.size=Pt(8.5); r.font.color.rgb=RGBColor(255,255,255)
        _set_repeat_table_header(table.rows[0])
        for area in ["Overall experience", "Manager support", "Work environment", "Growth / career", "Compensation", "Reason for leaving", "Would recommend employer"]:
            cells=table.add_row().cells
            for c in cells: _set_cell_border(c); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cells[0].text=area; cells[1].text="[ ] 1  [ ] 2  [ ] 3  [ ] 4  [ ] 5"; cells[2].text="[COMMENTS]"
            for c in cells:
                for r in c.paragraphs[0].runs: r.font.size=Pt(8.5)
        doc.add_paragraph("Additional comments: ________________________________________________________________")
        doc.add_paragraph("________________________________________________________________________________")
    else:
        _add_signature(doc)
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()


def _resume_clean_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _resume_json_from_ai(text):
    """Extract JSON from the model while tolerating a fenced JSON response."""
    cleaned = _resume_clean_text(text)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return None
    return None


def _docx_add_resume_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(str(text).upper())
    r.bold = True
    r.font.name = "Aptos Display"
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(37, 99, 235)
    line = doc.add_paragraph()
    line.paragraph_format.space_after = Pt(4)
    rr = line.add_run("────────────────────────────────────────────────────────")
    rr.font.size = Pt(4.5)
    rr.font.color.rgb = RGBColor(191, 219, 254)


def _docx_add_resume_bullets(doc, values):
    if not isinstance(values, list):
        return
    for value in values:
        if not str(value).strip():
            continue
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.first_line_indent = Inches(-0.12)
        r = p.add_run(str(value).strip())
        r.font.name = "Aptos"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(45, 55, 72)


def _docx_add_resume_entries(doc, entries):
    if not isinstance(entries, list):
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        title = str(entry.get("title", "")).strip()
        organization = str(entry.get("organization", "")).strip()
        dates = str(entry.get("dates", "")).strip()
        location = str(entry.get("location", "")).strip()
        if title:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(title)
            r.bold = True; r.font.name = "Aptos Display"; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(37, 45, 63)
            meta = " • ".join([x for x in [organization, location, dates] if x])
            if meta:
                r2 = p.add_run("  " + meta)
                r2.italic = True; r2.font.name = "Aptos"; r2.font.size = Pt(8.8); r2.font.color.rgb = RGBColor(91, 105, 125)
        _docx_add_resume_bullets(doc, entry.get("bullets", []))


def professional_resume_docx(data):
    """Build a clean ATS-friendly resume without Nexora branding in the file."""
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)
    _style_document(doc)

    name = str(data.get("name", "PROFESSIONAL RESUME")).strip() or "PROFESSIONAL RESUME"
    role = str(data.get("target_title", "")).strip()
    contact = [str(data.get(k, "")).strip() for k in ["phone", "email", "location", "linkedin"]]
    contact = [x for x in contact if x]

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(name)
    r.bold = True; r.font.name = "Aptos Display"; r.font.size = Pt(21); r.font.color.rgb = RGBColor(23, 59, 108)
    if role:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(2)
        r = p.add_run(role); r.bold=True; r.font.name="Aptos"; r.font.size=Pt(11); r.font.color.rgb=RGBColor(37,99,235)
    if contact:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(6)
        r = p.add_run("  |  ".join(contact)); r.font.name="Aptos"; r.font.size=Pt(8.5); r.font.color.rgb=RGBColor(91,105,125)

    summary = str(data.get("summary", "")).strip()
    if summary:
        _docx_add_resume_heading(doc, "Professional Summary")
        p = doc.add_paragraph(summary); p.paragraph_format.space_after = Pt(3)
        for r in p.runs: r.font.name="Aptos"; r.font.size=Pt(9.5); r.font.color.rgb=RGBColor(45,55,72)

    skills = data.get("skills", [])
    if isinstance(skills, list) and skills:
        _docx_add_resume_heading(doc, "Core Skills")
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(3)
        r = p.add_run("  •  ".join([str(x).strip() for x in skills if str(x).strip()]))
        r.font.name="Aptos"; r.font.size=Pt(9.2); r.font.color.rgb=RGBColor(45,55,72)

    if data.get("experience"):
        _docx_add_resume_heading(doc, "Professional Experience")
        _docx_add_resume_entries(doc, data.get("experience"))
    if data.get("projects"):
        _docx_add_resume_heading(doc, "Selected Projects")
        _docx_add_resume_entries(doc, data.get("projects"))
    if data.get("education"):
        _docx_add_resume_heading(doc, "Education")
        _docx_add_resume_entries(doc, data.get("education"))
    if data.get("certifications"):
        _docx_add_resume_heading(doc, "Certifications")
        _docx_add_resume_bullets(doc, data.get("certifications"))
    if data.get("achievements"):
        _docx_add_resume_heading(doc, "Achievements")
        _docx_add_resume_bullets(doc, data.get("achievements"))
    if data.get("additional"):
        _docx_add_resume_heading(doc, "Additional Information")
        _docx_add_resume_bullets(doc, data.get("additional"))

    # Neutral resume footer; deliberately no Nexora promotional text.
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run("Professional Resume  •  Candidate-provided information only")
    fr.font.name="Aptos"; fr.font.size=Pt(7.5); fr.font.color.rgb=RGBColor(120,130,145)

    output = io.BytesIO(); doc.save(output); return output.getvalue()


def improve_resume(resume_file, target_role, analysis, resume_file_type="application/pdf", resume_file_name="resume.pdf"):
    prompt = f"""
You are Nexora's senior executive resume writer and ATS optimization specialist.
Create a highly professional, ATS-friendly resume from the uploaded candidate resume.
Target role: {target_role or 'Not specified'}

Existing resume analysis:
{analysis or 'Not available'}

Your task is to FIX the weaknesses identified in the analysis while preserving factual accuracy.
You may rewrite weak wording, improve structure, remove repetition, strengthen action language,
make achievements clearer, improve keyword alignment, and create a concise professional summary.
You MUST NOT invent employers, job titles, dates, degrees, certifications, technologies, metrics,
responsibilities, awards or achievements. Never create a number that was not present in the source.
If a useful field is absent, leave it empty rather than guessing.
Keep the candidate's actual career history intact.

Return ONLY valid JSON in this exact shape:
{{
  "name":"",
  "target_title":"",
  "phone":"",
  "email":"",
  "location":"",
  "linkedin":"",
  "summary":"",
  "skills":[""],
  "experience":[{{"title":"","organization":"","dates":"","location":"","bullets":[""]}}],
  "projects":[{{"title":"","organization":"","dates":"","location":"","bullets":[""]}}],
  "education":[{{"title":"","organization":"","dates":"","location":"","bullets":[""]}}],
  "certifications":[""],
  "achievements":[""],
  "additional":[""]
}}

Use only information found in the uploaded resume. Make the finished resume concise, modern,
professional and ATS-readable. Rewrite bullet points into strong action-oriented language when
supported by the source. Remove decorative symbols, tables, columns, photos and unnecessary
personal details. Do not include a cover letter. Do not mention Nexora in the resume content.
"""
    # Rebuild a lightweight upload object from session-persisted bytes so the
    # improvement step still works after Streamlit reruns.
    if isinstance(resume_file, (bytes, bytearray)):
        upload = io.BytesIO(bytes(resume_file))
        upload.name = resume_file_name or "resume.pdf"
        upload.type = resume_file_type or "application/pdf"
        resume_file = upload
    raw = ai_text(prompt, resume_file)
    if not raw:
        return None, None
    data = _resume_json_from_ai(raw)
    if not isinstance(data, dict):
        st.error("Nexora received an unexpected resume format. Please try again.")
        return None, None
    try:
        output = professional_resume_docx(data)
    except Exception as error:
        st.error("The improved resume could not be formatted.")
        with st.expander("Technical details"): st.code(str(error))
        return None, None
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", str(data.get("name") or "professional_resume")).strip("_") or "professional_resume"
    return output, f"{safe_name}_professional_resume.docx"


def reset_workspace():
    for key, value in DEFAULTS.items():
        st.session_state[key] = [] if isinstance(value, list) else value

def analyze_document(file):
    prompt = """
You are Nexora, a professional AI document assistant.
Read and understand the uploaded document carefully.
Return:
## Executive Summary
Give a concise explanation of what the document is about.
## Key Information
List the most important facts including names, dates, amounts, organizations, reference numbers, addresses, important terms and other critical information.
## Key Takeaways
Give the most useful points a person should know.
## Risks and Concerns
Identify missing information, potential risks, inconsistencies, unusual clauses and items requiring verification. If none are obvious, say so.
## Suggested Questions
Give 5 useful questions the user could ask about this document.
Rules: Do not invent information. Use only information present in the document. Preserve dates and numbers accurately. If unclear, say so. Keep the result professional and easy to scan.
"""
    return client.interactions.create(model=MODEL, input=[{"type":"text","text":prompt}, make_document_part(file)], store=True, generation_config={"thinking_level":"minimal"})

def process_document(file):
    try:
        with st.spinner("Nexora is understanding your document..."):
            interaction = analyze_document(file)
        interaction_id = getattr(interaction, "id", None)
        output = getattr(interaction, "output_text", "")
        if not interaction_id or not output:
            st.error("Nexora did not receive a valid Gemini response.")
            return False
        st.session_state.interaction_id = interaction_id
        st.session_state.summary = output
        st.session_state.document_name = file.name
        st.session_state.document_type = get_mime_type(file)
        st.session_state.document_bytes = file.getvalue()
        st.session_state.document_ready = True
        st.session_state.messages = []
        st.session_state.extracted_information = None
        st.session_state.extracted_line_items = None
        st.session_state.analysis_result = None
        st.session_state.active_view = "Summary"
        return True
    except Exception as error:
        text = str(error)
        st.error("Nexora could not analyze the document.")
        if "429" in text: st.warning("The Gemini request limit was reached. Please wait and try again.")
        elif "500" in text or "503" in text: st.warning("Gemini is temporarily busy. Please try again.")
        else: st.warning("Please try the Analyze Document button again.")
        with st.expander("Technical details"): st.code(text)
        return False

def ask_document(question, placeholder):
    try:
        stream = client.interactions.create(model=MODEL, previous_interaction_id=st.session_state.interaction_id, input=question, store=True, stream=True, generation_config={"thinking_level":"minimal"})
        answer, latest_id = "", None
        for event in stream:
            event_type = getattr(event, "event_type", None)
            if event_type == "step.delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "type", None) == "text":
                    text = getattr(delta, "text", "")
                    if text:
                        answer += text
                        placeholder.markdown(answer)
            elif event_type == "interaction.complete":
                latest_id = getattr(event, "id", None)
        if latest_id: st.session_state.interaction_id = latest_id
        return answer
    except Exception as error:
        st.error("Nexora could not answer the question.")
        with st.expander("Technical details"): st.code(str(error))
        return ""

def extract_data():
    prompt = """
Extract structured information from the document. Return ONLY valid JSON:
{"document_information":[{"field":"","value":""}],"line_items":[{"description":"","quantity":"","unit_price":"","amount":""}]}
Rules: extract only information present; never invent; use empty strings when unavailable; preserve dates and numbers; valid JSON only.
"""
    try:
        with st.spinner("Extracting structured information..."):
            response = client.interactions.create(model=MODEL, previous_interaction_id=st.session_state.interaction_id, input=prompt, store=True, generation_config={"thinking_level":"minimal"})
        st.session_state.interaction_id = response.id
        text = getattr(response, "output_text", "")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            st.error("Nexora could not extract structured data.")
            return
        data = json.loads(match.group())
        st.session_state.extracted_information = data.get("document_information", [])
        st.session_state.extracted_line_items = data.get("line_items", [])
        st.session_state.active_view = "Extract Data"
        st.rerun()
    except Exception as error:
        st.error("Data extraction failed.")
        with st.expander("Technical details"): st.code(str(error))

def run_deep_analysis():
    prompt = """
Perform a detailed analysis of this document. Focus on important risks, missing information, dates, amounts, unusual clauses, inconsistencies, information requiring human attention and practical next steps. Do not invent anything. Clearly distinguish facts from observations. Use clear headings and bullet points.
"""
    try:
        with st.spinner("Nexora is performing deeper analysis..."):
            response = client.interactions.create(model=MODEL, previous_interaction_id=st.session_state.interaction_id, input=prompt, store=True, generation_config={"thinking_level":"minimal"})
        st.session_state.interaction_id = response.id
        st.session_state.analysis_result = getattr(response, "output_text", "")
        st.session_state.active_view = "Analyze"
        st.rerun()
    except Exception as error:
        st.error("Deep analysis failed.")
        with st.expander("Technical details"): st.code(str(error))

def create_excel():
    info_df = pd.DataFrame(st.session_state.extracted_information or [])
    items_df = pd.DataFrame(st.session_state.extracted_line_items or [])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if not info_df.empty: info_df.to_excel(writer, sheet_name="Document Information", index=False)
        if not items_df.empty: items_df.to_excel(writer, sheet_name="Line Items", index=False)
    return output.getvalue()


# ============================================================
# NEXORA PRODUCT NAVIGATION
# ============================================================
if "main_section" not in st.session_state:
    st.session_state.main_section = "Documents"

logo, home_nav, hr_nav, docs_nav, pricing_nav, account = st.columns(
    [2.25, .75, 1.25, 1.05, .9, 1.35], gap="small", vertical_alignment="center"
)

with logo:
    st.markdown("# ✦ NEXORA")
    st.caption("AI WORK • DOCUMENTS • CAREER")

with home_nav:
    if st.button("Home", use_container_width=True, key="nav_home"):
        st.session_state.main_section = "Documents"
        st.session_state.pricing_open = False
        st.rerun()

with hr_nav:
    if st.button("HR & Career", use_container_width=True, key="nav_hr"):
        st.session_state.main_section = "HR"
        st.session_state.pricing_open = False
        st.rerun()

with docs_nav:
    if st.button("Documents", use_container_width=True, key="nav_documents"):
        st.session_state.main_section = "Documents"
        st.session_state.pricing_open = False
        st.rerun()

with pricing_nav:
    if st.button("Pricing", use_container_width=True, key="nav_pricing"):
        st.session_state.pricing_open = not st.session_state.pricing_open
        st.rerun()

with account:
    if logged_in():
        a, b = st.columns([2.4, 1], gap="small")
        with a:
            st.caption(f"● {display_name()}")
        with b:
            if st.button("↪", help="Log out", key="nav_logout"):
                st.logout()
    else:
        st.caption("Free access")

st.divider()

# ============================================================
# PRICING / PAYMENT LOGIN GATE
# ============================================================
if st.session_state.pricing_open:
    st.markdown("# ✦ Nexora Plans")
    st.caption("Explore Nexora freely. Login is requested only when you choose a paid plan.")

    free_col, pro_col = st.columns(2, gap="small", vertical_alignment="top")

    with free_col:
        with st.container(border=True):
            st.markdown("## 🆓 Free")
            st.markdown("### Explore Nexora")
            st.caption("No account required for the current free workflows.")
            for item in [
                "AI document summary",
                "Document Q&A",
                "Structured data extraction",
                "HR salary calculators",
                "Resume / JD / offer analysis",
                "Starter HR templates",
            ]:
                st.write(f"✓ {item}")
            st.button("Current plan", disabled=True, use_container_width=True, key="free_plan")

    with pro_col:
        with st.container(border=True):
            st.markdown("## ✦ Nexora Pro")
            st.markdown("### Paid plan")
            st.caption("Premium usage and future account-based features.")
            for item in [
                "Higher usage limits",
                "Premium document workflows",
                "Detailed HR & career reports",
                "Account-linked purchase",
                "Saved-document and calculation history",
            ]:
                st.write(f"✓ {item}")

            if not logged_in():
                st.info("Sign in is required only when you start checkout.")
                if st.button(
                    "G  Login & Continue to Checkout",
                    type="primary",
                    use_container_width=True,
                    key="pricing_login",
                ):
                    if auth_configured():
                        st.login()
                    else:
                        st.warning("Google login is not configured yet.")
            else:
                st.success(f"Signed in as {display_name()}.")
                st.button(
                    "Continue to Payment",
                    type="primary",
                    use_container_width=True,
                    key="continue_payment",
                )
                st.caption(
                    "Google Login is ready. The payment gateway can be connected "
                    "to this button in the next phase."
                )

    st.divider()

# ============================================================
# HR & CAREER HUB
# ============================================================
def render_hr_hub():
    st.caption("✦ NEXORA HR & CAREER • SALARY • CAREER • HR TOOLS")
    st.markdown("# HR work, career decisions. ✦ **Made simpler.**")
    st.write("Salary calculators, career analysis and practical HR templates — built into Nexora.")

    section = st.radio(
        "HR toolkit",
        ["Salary & HR Calculators", "AI Career Tools", "HR Templates"],
        horizontal=True,
        label_visibility="collapsed",
        key="hr_section",
    )

    # ============================================================
    # SALARY & HR CALCULATORS
    # ============================================================
    if section == "Salary & HR Calculators":
        st.markdown("## 💰 Salary & HR Calculators")
        st.caption("Free calculators first. Later, detailed reports and saved calculations can become Nexora Pro features.")

        calculator = st.selectbox(
            "Choose a calculator",
            [
                "CTC → Take-Home Salary",
                "Salary Increment Calculator",
                "Gratuity Estimator",
                "Notice Period Salary Calculator",
            ],
        )

        if calculator == "CTC → Take-Home Salary":
            left, right = st.columns([1.1, 1], gap="small", vertical_alignment="top")
            with left:
                with st.container(border=True):
                    st.subheader("🧾 Enter your salary structure")
                    annual_ctc = st.number_input("Annual CTC (₹)", min_value=0.0, value=600000.0, step=10000.0)
                    basic_pct = st.number_input("Basic salary as % of CTC", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
                    variable_pct = st.number_input("Variable / bonus as % of CTC", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                    employee_pf_rate = st.number_input("Employee PF rate on Basic (%)", min_value=0.0, max_value=20.0, value=12.0, step=0.5)
                    monthly_pt = st.number_input("Professional tax / other fixed monthly deduction (₹)", min_value=0.0, value=200.0, step=50.0)
                    other_monthly = st.number_input("Other monthly deductions (₹)", min_value=0.0, value=0.0, step=100.0)
                    pf_cap = st.number_input("PF wage base cap (₹/month, 0 = no cap)", min_value=0.0, value=15000.0, step=1000.0)

            basic_annual = annual_ctc * basic_pct / 100
            variable_annual = annual_ctc * variable_pct / 100
            fixed_annual = max(annual_ctc - variable_annual, 0)
            gross_annual = fixed_annual
            basic_monthly = basic_annual / 12
            pf_base = min(basic_monthly, pf_cap) if pf_cap > 0 else basic_monthly
            employee_pf = pf_base * employee_pf_rate / 100
            monthly_gross = gross_annual / 12
            take_home = max(monthly_gross - employee_pf - monthly_pt - other_monthly, 0)

            with right:
                with st.container(border=True):
                    st.subheader("📊 Estimated result")
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Monthly gross", money(monthly_gross))
                        st.metric("Employee PF", money(employee_pf))
                    with m2:
                        st.metric("Estimated take-home", money(take_home))
                        st.metric("Annual fixed pay", money(fixed_annual))
                    st.divider()
                    st.write(f"**Basic:** {money(basic_monthly)}/month")
                    st.write(f"**Variable / bonus:** {money(variable_annual)}/year")
                    st.write(f"**Other fixed deductions:** {money(monthly_pt + other_monthly)}/month")
                    st.info("This is an estimate, not a payroll statement. Actual take-home can differ because of tax regime, employer policy, PF treatment, insurance, professional tax and other deductions.")
                    st.caption("PF defaults are configurable. EPFO's published contribution information describes 12% as the standard employee rate in covered establishments, with exceptions and wage-ceiling rules. Treat the inputs above as configurable payroll assumptions.")

        elif calculator == "Salary Increment Calculator":
            c1, c2 = st.columns(2, gap="small")
            with c1:
                with st.container(border=True):
                    st.subheader("📈 Current salary")
                    current = st.number_input("Current annual CTC (₹)", min_value=0.0, value=600000.0, step=10000.0)
                    increment = st.number_input("Increment (%)", min_value=-100.0, max_value=500.0, value=10.0, step=0.5)
                    current_monthly = current / 12
            with c2:
                with st.container(border=True):
                    new_ctc = current * (1 + increment / 100)
                    increase = new_ctc - current
                    st.subheader("🚀 New salary")
                    st.metric("New annual CTC", money(new_ctc))
                    st.metric("Annual increase", money(increase))
                    st.metric("New monthly CTC", money(new_ctc / 12))
                    st.caption(f"Current monthly CTC: {money(current_monthly)}")

            st.divider()
            st.write("### Quick comparison")
            rows = []
            for pct in [5, 8, 10, 12, 15, 20, 25, 30]:
                new_value = current * (1 + pct / 100)
                rows.append({"Increment": f"{pct}%", "New CTC": money(new_value), "Monthly CTC": money(new_value / 12), "Annual increase": money(new_value - current)})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        elif calculator == "Gratuity Estimator":
            c1, c2 = st.columns([1.05, 1], gap="small")
            with c1:
                with st.container(border=True):
                    st.subheader("🏆 Gratuity inputs")
                    last_wage = st.number_input("Last drawn monthly wages used for calculation (₹)", min_value=0.0, value=30000.0, step=1000.0)
                    years = st.number_input("Completed years of service", min_value=0, max_value=60, value=5, step=1)
                    extra_months = st.number_input("Extra months", min_value=0, max_value=11, value=0, step=1)
                    apply_rounding = st.checkbox("Treat 6+ extra months as one additional year", value=True)
                    cap = st.number_input("Optional gratuity cap (₹, 0 = no cap)", min_value=0.0, value=0.0, step=10000.0)
            effective_years = years + (1 if apply_rounding and extra_months >= 6 else 0)
            raw_gratuity = last_wage * 15 / 26 * effective_years
            final_gratuity = min(raw_gratuity, cap) if cap > 0 else raw_gratuity
            with c2:
                with st.container(border=True):
                    st.subheader("💡 Estimated gratuity")
                    st.metric("Estimated amount", money(final_gratuity))
                    st.write(f"**Formula:** {money(last_wage)} × 15 ÷ 26 × {effective_years} year(s)")
                    st.info("This is an estimate. Gratuity eligibility and calculation can depend on the applicable law, employee category, continuity of service and the reason for separation. Current government labour-code material describes gratuity at 15 days' wages for each completed year, subject to the notified maximum, and includes special rules for fixed-term employees. Verify the applicable rule before relying on the result.")

        else:
            c1, c2 = st.columns(2, gap="small")
            with c1:
                with st.container(border=True):
                    st.subheader("📅 Notice period")
                    monthly_salary = st.number_input("Monthly salary (₹)", min_value=0.0, value=50000.0, step=1000.0)
                    notice_days = st.number_input("Notice period (days)", min_value=0, max_value=365, value=30, step=1)
                    working_days = st.number_input("Working days used for daily-rate estimate", min_value=1, max_value=31, value=30, step=1)
            with c2:
                with st.container(border=True):
                    daily_rate = monthly_salary / working_days if working_days else 0
                    estimated = daily_rate * notice_days
                    st.subheader("💼 Estimate")
                    st.metric("Daily salary basis", money(daily_rate))
                    st.metric("Notice-period salary", money(estimated))
                    st.info("Notice pay depends on the employment contract, applicable law and company policy. This calculator is only a simple estimate.")

    # ============================================================
    # AI CAREER TOOLS
    # ============================================================
    elif section == "AI Career Tools":
        st.markdown("## 🤖 AI Career Tools")
        st.caption("These are the first three AI products in the Nexora HR roadmap: Resume Analyzer, Job Description Analyzer and Offer Letter Analyzer.")

        tool = st.selectbox("Choose an AI career tool", ["Resume Analyzer", "Job Description Analyzer", "Offer Letter Analyzer"])

        if tool == "Resume Analyzer":
            st.subheader("📄 Resume Analyzer")
            st.write("Upload a resume and get an ATS-style review, strengths, gaps and targeted improvement suggestions.")
            resume = st.file_uploader("Upload resume", type=["pdf", "png", "jpg", "jpeg"], key="resume_upload")
            target_role = st.text_input("Target role (optional)", placeholder="e.g. HR Manager, Talent Acquisition Specialist", key="resume_target_role_input")
            if resume:
                valid, msg = validate_ai_file(resume)
                if not valid:
                    st.error(msg)
                elif st.button("✦ Analyze Resume", type="primary", use_container_width=True, key="analyze_resume_btn"):
                    prompt = f"""
    You are Nexora HR, an expert Indian recruitment and career assistant.
    Analyze the uploaded resume carefully. Target role: {target_role or 'Not specified'}.
    Return a practical report with these sections:
    1. Overall Resume Score / 100
    2. Executive Assessment
    3. ATS Readiness
    4. Strongest Skills and Evidence
    5. Missing or Weak Areas
    6. Experience & Achievement Quality
    7. Keywords to Add
    8. Formatting / Clarity Issues
    9. Role Match Assessment
    10. Top 10 Changes to Improve Interview Chances
    11. Improved Professional Summary
    12. 5 Suggested Interview Questions
    Do not invent experience, qualifications or achievements. If information is missing, say so.
    """
                    with st.spinner("Nexora is analyzing the resume..."):
                        result = ai_text(prompt, resume)
                    if result:
                        st.session_state.resume_analysis = result
                        st.session_state.resume_file_bytes = resume.getvalue()
                        st.session_state.resume_file_name = resume.name
                        st.session_state.resume_file_type = get_mime_type(resume)
                        st.session_state.resume_target_role = target_role
                        st.session_state.improved_resume_bytes = None
                        st.session_state.improved_resume_name = None
                        st.session_state.resume_fix_paid_demo = False

            if st.session_state.resume_analysis:
                st.divider()
                st.subheader("📊 Resume Assessment")
                st.markdown(st.session_state.resume_analysis)
                st.divider()
                st.subheader("🚀 Fix My Resume")
                st.caption("Temporary payment simulation for visual testing. No real payment is processed.")
                st.info("Nexora will rewrite the weak areas, improve ATS readability and create a polished, editable professional resume — without inventing candidate information.")
                pay_col, status_col = st.columns([1, 1.6], vertical_alignment="center")
                with pay_col:
                    if st.button("💳 Pay ₹99 (Temporary)", type="primary", use_container_width=True, key="resume_pay_demo"):
                        with st.spinner("Payment confirmed (demo). Nexora is rebuilding your resume..."):
                            improved_bytes, improved_name = improve_resume(
                                st.session_state.resume_file_bytes,
                                st.session_state.resume_target_role,
                                st.session_state.resume_analysis,
                                st.session_state.resume_file_type,
                                st.session_state.resume_file_name,
                            )
                        if improved_bytes:
                            st.session_state.improved_resume_bytes = improved_bytes
                            st.session_state.improved_resume_name = improved_name
                            st.session_state.resume_fix_paid_demo = True
                with status_col:
                    if st.session_state.resume_fix_paid_demo:
                        st.success("Demo payment successful — your improved resume is ready.")
                    else:
                        st.caption("One-time demo price only. The real payment gateway will be connected later.")

                if st.session_state.improved_resume_bytes:
                    st.markdown("### ✨ Your Professional Resume")
                    st.success("The identified weaknesses have been addressed where the source resume provided enough factual information.")
                    st.download_button(
                        "⬇️ Download Professional Resume (Word)",
                        data=st.session_state.improved_resume_bytes,
                        file_name=st.session_state.improved_resume_name or "professional_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="download_improved_resume",
                    )
                    st.caption("The downloaded resume contains no Nexora promotional branding.")

        elif tool == "Job Description Analyzer":
            st.subheader("🎯 Job Description Analyzer")
            st.write("Paste a job description and Nexora will identify requirements, hidden expectations and the keywords a candidate should address.")
            jd = st.text_area("Paste the job description", height=300, placeholder="Paste the complete job description here...")
            resume_context = st.text_area("Optional: paste your resume summary", height=160, placeholder="Paste your profile/resume summary for a match analysis...")
            if st.button("✦ Analyze Job Description", type="primary", use_container_width=True):
                if len(jd.strip()) < 40:
                    st.warning("Please paste a fuller job description so the analysis is useful.")
                else:
                    prompt = f"""
    You are Nexora HR, an expert recruitment analyst.
    Analyze this job description:
    ---
    {jd}
    ---
    Candidate resume/profile context (optional):
    ---
    {resume_context or 'Not provided'}
    ---
    Return:
    1. Role summary
    2. Must-have requirements
    3. Nice-to-have requirements
    4. Technical / functional skills
    5. Soft skills
    6. Experience and education expectations
    7. Important ATS keywords
    8. Hidden or implied expectations
    9. Candidate match assessment if profile was provided
    10. Missing information / questions to ask the employer
    11. Resume keywords and bullet themes the candidate should emphasize
    Do not invent information.
    """
                    with st.spinner("Nexora is reading the job description..."):
                        result = ai_text(prompt)
                    if result:
                        st.markdown(result)

        else:
            st.subheader("📑 Offer Letter Analyzer")
            st.write("Upload an offer letter and Nexora will highlight salary structure, notice period, probation, variable pay and clauses worth reviewing.")
            offer = st.file_uploader("Upload offer letter", type=["pdf", "png", "jpg", "jpeg"], key="offer_upload")
            if offer:
                valid, msg = validate_ai_file(offer)
                if not valid:
                    st.error(msg)
                elif st.button("✦ Analyze Offer Letter", type="primary", use_container_width=True):
                    prompt = """
    You are Nexora HR, an employment-document review assistant for India.
    Read the uploaded offer letter carefully and produce a plain-English decision-support report.
    Return:
    1. Executive summary
    2. Employer / role / location / joining date
    3. Fixed compensation
    4. Variable compensation and performance-linked amounts
    5. Deductions / benefits mentioned
    6. Probation period
    7. Notice period
    8. Working hours / shifts / location conditions
    9. Leave / benefits mentioned
    10. Important restrictive or unusual clauses
    11. Termination / separation clauses
    12. Bond / service agreement / repayment clauses, if any
    13. Confidentiality / IP / non-compete language, if any
    14. Missing or unclear information
    15. Questions the candidate should ask HR before accepting
    16. Overall review: Favorable / Needs clarification / High attention, with reasons
    Do not give legal advice or make unsupported legal conclusions. Quote only short phrases when necessary and otherwise explain in your own words. Do not invent information.
    """
                    with st.spinner("Nexora is reviewing the offer letter..."):
                        result = ai_text(prompt, offer)
                    if result:
                        st.markdown(result)

    # ============================================================
    # HR TEMPLATES
    # ============================================================
    else:
        st.markdown("## 📚 HR Templates")
        st.caption("Professional, editable HR drafts with a clean corporate layout. Replace bracketed fields and review against your company policy before issue.")

        template = st.selectbox(
            "Choose a template",
            [
                "Offer Letter", "Appointment Letter", "Salary Increment Letter", "Promotion Letter",
                "Experience Certificate", "Relieving Letter", "Employee Warning Letter", "Exit Interview Form",
            ],
            key="hr_template_select",
        )

        templates = {
            "Offer Letter": {
                "subtitle":"Employment offer letter • editable draft",
                "metadata":[("Date","[DATE]"),("Reference","[REFERENCE NO.]"),("Candidate","[EMPLOYEE NAME]"),("Designation","[DESIGNATION]")],
                "sections":[
                    ("01  Offer of Employment",["Dear [EMPLOYEE NAME],","We are pleased to offer you employment with [COMPANY NAME] for the position of [DESIGNATION], subject to the terms set out in this letter and the applicable employment policies of the organization.","Proposed date of joining: [JOINING DATE]","Reporting location / work arrangement: [LOCATION / WORK ARRANGEMENT]"]),
                    ("02  Compensation & Benefits",["Annual CTC / gross compensation: [CTC]","The detailed compensation structure, benefits and applicable deductions will be communicated separately / attached as applicable."]),
                    ("03  Conditions of Employment",["This offer is subject to satisfactory completion of applicable background / reference checks, submission of required documents and compliance with company policies.","The final employment relationship will be governed by the appointment / employment documentation issued by the company and applicable law."]),
                    ("04  Acceptance",["Please sign and return a copy of this letter by [ACCEPTANCE DATE] to confirm your acceptance of the offer.","We look forward to welcoming you to [COMPANY NAME]."]),
                ]},
            "Appointment Letter": {
                "subtitle":"Formal appointment letter • editable draft",
                "metadata":[("Date","[DATE]"),("Employee ID","[EMPLOYEE ID]"),("Employee","[EMPLOYEE NAME]"),("Designation","[DESIGNATION]")],
                "sections":[
                    ("01  Appointment",["Dear [EMPLOYEE NAME],","You are appointed as [DESIGNATION] in [DEPARTMENT] with effect from [DATE]. We are pleased to have you join [COMPANY NAME]."]),
                    ("02  Place & Nature of Work",["Primary work location: [LOCATION]","Reporting manager: [MANAGER]","The role, responsibilities and reasonable work arrangements may be updated in line with business requirements and company policy."]),
                    ("03  Compensation",["Your annual CTC / gross compensation will be [CTC]. The detailed salary structure and eligible benefits are as communicated separately."]),
                    ("04  Probation",["Probation period: [PERIOD]. Confirmation will be subject to performance, conduct, business requirements and the applicable company policy."]),
                    ("05  Notice & Separation",["Notice period: [DAYS] days, subject to the employment contract, company policy and applicable law."]),
                    ("06  Acknowledgement",["Please sign below to acknowledge receipt and acceptance of the appointment terms."]),
                ]},
            "Salary Increment Letter": {
                "subtitle":"Compensation revision communication • editable draft",
                "metadata":[("Date","[DATE]"),("Employee ID","[EMPLOYEE ID]"),("Employee","[EMPLOYEE NAME]"),("Designation","[DESIGNATION]")],
                "sections":[
                    ("01  Compensation Revision",["Dear [EMPLOYEE NAME],","We are pleased to inform you that, in recognition of your contribution and performance, your compensation has been revised with effect from [EFFECTIVE DATE]."]),
                    ("02  Compensation Summary",["Previous annual CTC / gross: [OLD CTC]","Revised annual CTC / gross: [NEW CTC]","Increment: [PERCENTAGE]%"]),
                    ("03  Closing",["We appreciate your contribution to [COMPANY NAME] and look forward to your continued growth and success."]),
                ]},
            "Promotion Letter": {
                "subtitle":"Promotion communication • editable draft",
                "metadata":[("Date","[DATE]"),("Employee ID","[EMPLOYEE ID]"),("Employee","[EMPLOYEE NAME]"),("Effective Date","[EFFECTIVE DATE]")],
                "sections":[
                    ("01  Promotion",["Dear [EMPLOYEE NAME],","We are pleased to inform you that you have been promoted to [NEW DESIGNATION], effective [EFFECTIVE DATE], in recognition of your contribution and performance."]),
                    ("02  Role Details",["Department / Function: [DEPARTMENT]","Reporting manager: [MANAGER]","Primary responsibilities: [BRIEF ROLE SUMMARY]"]),
                    ("03  Compensation",["Revised annual CTC / gross: [CTC]","The detailed compensation structure and applicable benefits will be communicated separately."]),
                    ("04  Congratulations",["Congratulations on this achievement. We wish you continued success in your expanded role."]),
                ]},
            "Experience Certificate": {
                "subtitle":"Employment experience certificate • editable draft",
                "metadata":[("Date","[DATE]"),("Reference","[REFERENCE NO.]"),("Employee","[EMPLOYEE NAME]"),("Employee ID","[EMPLOYEE ID]")],
                "sections":[
                    ("01  To Whom It May Concern",["This is to certify that [EMPLOYEE NAME] was employed with [COMPANY NAME] as [DESIGNATION] from [START DATE] to [END DATE]."]),
                    ("02  Employment Details",["Department / Function: [DEPARTMENT / FUNCTION]","Location: [LOCATION]","The above information is issued based on the employment records available with the organization."]),
                    ("03  Closing",["We wish [EMPLOYEE NAME] all the best in future professional endeavors."]),
                ]},
            "Relieving Letter": {
                "subtitle":"Employee separation confirmation • editable draft",
                "metadata":[("Date","[DATE]"),("Reference","[REFERENCE NO.]"),("Employee","[EMPLOYEE NAME]"),("Employee ID","[EMPLOYEE ID]")],
                "sections":[
                    ("01  Relieving Confirmation",["Dear [EMPLOYEE NAME],","This is to confirm that you have been relieved from your services with [COMPANY NAME] effective [LAST WORKING DATE], following completion of the applicable separation formalities."]),
                    ("02  Handover & Clearance",["The required handover, asset return and clearance activities have been completed / are recorded as applicable in the organization's records."]),
                    ("03  Closing",["We thank you for your services and contribution during your association with [COMPANY NAME]. We wish you success in your future endeavors."]),
                ]},
            "Employee Warning Letter": {
                "subtitle":"Formal workplace warning • editable draft",
                "metadata":[("Date","[DATE]"),("Reference","[REFERENCE NO.]"),("Employee","[EMPLOYEE NAME]"),("Employee ID","[EMPLOYEE ID]")],
                "sections":[
                    ("01  Subject",["Subject: Formal Warning — [SUBJECT]"]),
                    ("02  Concern / Incident",["This letter is being issued regarding [FACTUAL DESCRIPTION OF ISSUE], observed / reported on [DATE(S)]. The concern has been discussed / documented as applicable."]),
                    ("03  Expected Improvement",["You are required to [CLEAR EXPECTATION] with immediate effect and to maintain the expected standard consistently.","Any supporting documents, examples or relevant policy references may be attached to this letter."]),
                    ("04  Review & Support",["Progress will be reviewed on [REVIEW DATE / PERIOD]. Please contact [MANAGER / HR] if you require clarification regarding the expectations set out above."]),
                    ("05  Important Review",["This draft should be adapted to the organization's disciplinary process, documented facts, applicable policy and applicable law before issue."]),
                ]},
            "Exit Interview Form": {
                "subtitle":"Structured employee exit feedback form",
                "metadata":[("Date","[INTERVIEW DATE]"),("Employee","[EMPLOYEE NAME]"),("Department","[DEPARTMENT]"),("Last Working Day","[DATE]")],
                "sections":[
                    ("01  Interview Details",["Interviewer: [INTERVIEWER NAME]","Designation: [DESIGNATION]","Tenure: [TENURE]"]),
                    ("02  Key Discussion Points",["Primary reason for leaving: [REASON]","Has another offer been accepted? [YES / NO / PREFER NOT TO SAY]","What did you value most about your experience? [RESPONSE]","What should the organization improve? [RESPONSE]","What could have influenced you to stay? [RESPONSE]"]),
                    ("03  Ratings",["Use the structured rating table below and add comments where useful."]),
                    ("04  Additional Notes",["HR / interviewer notes: [NOTES]"]),
                ]},
        }

        item = templates[template]
        c1, c2 = st.columns([1.45, 1], gap="small", vertical_alignment="top")
        with c1:
            with st.container(border=True):
                st.subheader(f"📝 {template}")
                st.caption(item["subtitle"])
                st.markdown("**Professional document preview**")
                _metadata = item["metadata"]
                _sections = item["sections"]
                for label, value in _metadata:
                    st.write(f"**{label}:** {value}")
                st.divider()
                for heading, lines in _sections:
                    st.markdown(f"**{heading}**")
                    for line in lines:
                        st.write(line)
                if template == "Exit Interview Form":
                    st.markdown("**Rating areas:** Overall experience · Manager support · Work environment · Growth · Compensation · Reason for leaving · Would recommend")
        with c2:
            with st.container(border=True):
                st.subheader("⬇️ Professional Word draft")
                st.write("Clean corporate formatting, consistent typography, structured sections and signature area — ready to customize.")
                content = docx_bytes(template, item["subtitle"], item["sections"], metadata=item["metadata"], form=(template == "Exit Interview Form"))
                filename = re.sub(r"[^a-z0-9]+", "_", template.lower()).strip("_") + "_template.docx"
                st.download_button(
                    "⬇️ Download Editable Word File",
                    data=content,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True,
                )
                st.success("✓ No Nexora promotional branding is inserted into the downloaded document.")
                st.info("Before issuing: replace all [BRACKETED] fields, verify names/dates/amounts, and review against company policy and applicable law.")

    # ============================================================
    st.divider()
    with st.container(border=True):
        st.subheader("🚀 Nexora HR roadmap")
        r1, r2, r3, r4 = st.columns(4, gap="small")
        for col, title, text in [
            (r1, "NOW", "Free salary calculators + HR templates + AI career analysis"),
            (r2, "NEXT", "SEO landing pages and shareable result pages"),
            (r3, "PRO", "Detailed reports, saved history and higher AI limits"),
            (r4, "SCALE", "HR teams, recruiter tools and business subscriptions"),
        ]:
            with col:
                st.markdown(f"**{title}**")
                st.caption(text)

    st.caption("✦ NEXORA HR  ·  Practical tools for work and career")

# ============================================================
# MAIN EXPERIENCE
# ============================================================
if st.session_state.main_section == "HR":
    render_hr_hub()

elif not st.session_state.document_ready:
    st.markdown("# Your documents. ✦ **Smarter with Nexora.**")
    st.write("Turn complex documents into clear summaries, structured data, intelligent analysis and instant answers.")

    category = st.radio(
        "Nexora tools",
        ["All", "Understand", "Chat", "Extract", "Analyze", "HR & Career"],
        horizontal=True,
        label_visibility="collapsed",
        key="document_home_category",
    )

    if category == "HR & Career":
        st.info("Nexora HR & Career brings salary calculators, career analysis and HR templates into the same workspace.")
        if st.button("✦ Open HR & Career Tools", type="primary", use_container_width=True, key="open_hr_home"):
            st.session_state.main_section = "HR"
            st.rerun()

    upload_col, feature_col = st.columns([1.55, 1], gap="small", vertical_alignment="top")
    with upload_col:
        with st.container(border=True):
            st.subheader("☁️ Start with a document")
            st.caption("Upload a PDF or image and build your AI workspace.")
            uploaded_file = st.file_uploader(
                "Choose a document",
                type=["pdf", "png", "jpg", "jpeg"],
                label_visibility="collapsed",
                max_upload_size=50,
            )
            if uploaded_file:
                valid, message = validate_file(uploaded_file)
                if not valid:
                    st.error(message)
                else:
                    st.success(f"✓ {uploaded_file.name} is ready")
                    if st.button("✦  Analyze Document", type="primary", use_container_width=True, key="home_analyze"):
                        if process_document(uploaded_file):
                            st.rerun()
            else:
                st.caption("PDF • PNG • JPG • JPEG   ·   Up to 50 MB")

    with feature_col:
        with st.container(border=True):
            st.subheader("✦ Nexora AI tools")
            for icon, title, text in [
                ("🧠", "AI Summary", "Understand long documents quickly."),
                ("💬", "Document Chat", "Ask questions directly about your file."),
                ("📊", "Data Extraction", "Turn content into structured data."),
                ("🔍", "Deep Analysis", "Find risks, gaps and important details."),
                ("💼", "HR & Career", "Salary tools, career analysis and HR templates."),
            ]:
                st.markdown(f"### {icon}  {title}")
                st.caption(text)

    st.subheader("Explore Nexora")
    cards = [
        ("🧠", "AI Summary", "Get the important points without reading every page."),
        ("💬", "Document Chat", "Ask natural-language questions about your document."),
        ("📊", "Extract Data", "Pull names, dates, amounts and line items into tables."),
        ("🔍", "Deep Analysis", "Spot risks, missing information and inconsistencies."),
        ("💼", "HR & Career", "Salary calculators, career analysis and practical HR tools."),
        ("📄", "Document View", "Keep the original document visible while working."),
    ]
    if category == "Understand":
        cards = [cards[0], cards[5]]
    elif category == "Chat":
        cards = [cards[1]]
    elif category == "Extract":
        cards = [cards[2]]
    elif category == "Analyze":
        cards = [cards[3]]
    elif category == "HR & Career":
        cards = [cards[4]]

    for start in range(0, len(cards), 3):
        cols = st.columns(3, gap="small")
        for col, (icon, title, text) in zip(cols, cards[start:start + 3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"## {icon}")
                    st.markdown(f"**{title}**")
                    st.caption(text)

    f1, f2, f3 = st.columns(3, gap="small")
    for col, title, text in [
        (f1, "⚡ Fast", "Optimized AI document and career workflows."),
        (f2, "🎯 Focused", "Useful results based on the information you provide."),
        (f3, "🛡️ Thoughtful", "Clear workflows designed for practical document work."),
    ]:
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(text)

else:
    header, new_doc = st.columns([5, 1], gap="small", vertical_alignment="center")
    with header:
        st.subheader(f"📄 {st.session_state.document_name}")
        st.caption("● Document analyzed and ready")
    with new_doc:
        if st.button("＋ New document", use_container_width=True, key="new_document"):
            reset_workspace()
            st.session_state.main_section = "Documents"
            st.rerun()

    selected = st.radio(
        "Document tools",
        ["Summary", "Extract Data", "Analyze"],
        index=["Summary", "Extract Data", "Analyze"].index(st.session_state.active_view),
        horizontal=True,
        label_visibility="collapsed",
        key="document_tools",
    )
    if selected != st.session_state.active_view:
        st.session_state.active_view = selected
        st.rerun()

    st.divider()

    document_column, chat_column = st.columns([1.65, 1], gap="small", vertical_alignment="top")
    with document_column:
        with st.container(border=True, height=760):
            st.subheader("📄 Document")
            st.caption(st.session_state.document_name)
            st.divider()
            if st.session_state.document_type == "application/pdf":
                try:
                    st.pdf(st.session_state.document_bytes, height=400)
                except Exception:
                    st.info("PDF preview is unavailable. The document is still available to Nexora.")
            elif st.session_state.document_type and st.session_state.document_type.startswith("image/"):
                st.image(st.session_state.document_bytes, use_container_width=True)

            st.divider()

            if st.session_state.active_view == "Summary":
                st.subheader("✨ AI Summary")
                if st.session_state.summary:
                    st.markdown(st.session_state.summary)

            elif st.session_state.active_view == "Extract Data":
                st.subheader("📊 Extracted Data")
                if st.session_state.extracted_information is None and st.session_state.extracted_line_items is None:
                    st.info("Extract structured information from this document.")
                    if st.button("📊  Extract Data", type="primary", use_container_width=True, key="extract_data_btn"):
                        extract_data()
                else:
                    info = st.session_state.extracted_information or []
                    items = st.session_state.extracted_line_items or []
                    if info:
                        st.write("**Document Information**")
                        st.dataframe(pd.DataFrame(info), use_container_width=True, hide_index=True)
                    if items:
                        st.write("**Line Items**")
                        st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
                    if info or items:
                        st.download_button(
                            "⬇️  Download Excel",
                            data=create_excel(),
                            file_name="nexora_extracted_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                    else:
                        st.warning("No structured information was found.")

            else:
                st.subheader("🔍 Deep Analysis")
                if not st.session_state.analysis_result:
                    st.info("Run deeper analysis to identify risks, missing information, inconsistencies and next steps.")
                    if st.button("🔍  Run Deep Analysis", type="primary", use_container_width=True, key="deep_analysis_btn"):
                        run_deep_analysis()
                else:
                    st.markdown(st.session_state.analysis_result)

    with chat_column:
        with st.container(border=True):
            st.subheader("✦ Nexora AI")
            st.caption("Ask questions and work with your document in real time.")

        with st.container(height=575, border=True):
            if not st.session_state.messages:
                st.info("Ask Nexora anything about this document.")
                st.write("**Try asking:**")
                for suggestion in [
                    "What is this document about?",
                    "What are the most important points?",
                    "Are there any risks I should know about?",
                    "What are the important dates and amounts?",
                    "Summarize this in simple language.",
                ]:
                    st.caption(f"• {suggestion}")
            else:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

        question = st.chat_input("Ask anything about this document...", key="nexora_chat_input")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                answer = ask_document(question, placeholder)
            if answer:
                st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

st.caption("✦ NEXORA  ·  AI Document Intelligence • HR & Career Intelligence")
