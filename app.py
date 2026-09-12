import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai

APP_NAME = "NEXORA"
MODEL = "gemini-3.5-flash-lite"
MAX_PDF_SIZE = 50 * 1024 * 1024
MAX_IMAGE_SIZE = 20 * 1024 * 1024

st.set_page_config(page_title="Nexora — AI Document Workspace", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# NEXORA VISUAL SYSTEM — native Streamlit UI, no visible HTML
# ============================================================
st.markdown(r"""
<style>
:root{--blue:#2563eb;--indigo:#4f46e5;--violet:#7c3aed;--cyan:#0891b2;--green:#16a34a;--orange:#f97316;--pink:#ec4899;--ink:#252637;--muted:#687083}
.stApp{background:radial-gradient(circle at 4% 0%,rgba(59,130,246,.23),transparent 24%),radial-gradient(circle at 96% 1%,rgba(236,72,153,.18),transparent 24%),radial-gradient(circle at 82% 42%,rgba(124,58,237,.13),transparent 27%),radial-gradient(circle at 15% 88%,rgba(6,182,212,.14),transparent 28%),linear-gradient(135deg,#f7fbff 0%,#f8f5ff 48%,#f3fbff 100%);min-height:100vh}
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
.stButton>button[kind="primary"]{color:white!important;border:none!important;background:linear-gradient(100deg,#2563eb,#4f46e5 48%,#8b5cf6)!important;box-shadow:0 9px 25px rgba(79,70,229,.24)}
.stButton>button[kind="primary"]:hover{background:linear-gradient(100deg,#1d4ed8,#4338ca 48%,#7c3aed)!important;box-shadow:0 12px 30px rgba(79,70,229,.30)}
div[role="radiogroup"]{gap:.3rem!important;padding:.18rem!important;background:rgba(255,255,255,.72);border:1px solid rgba(148,163,184,.2);border-radius:14px;box-shadow:0 5px 20px rgba(37,52,90,.035)}
div[role="radiogroup"] label{border-radius:10px!important;padding:.3rem .78rem!important;font-weight:700!important}
[data-testid="stChatMessage"]{border-radius:14px!important;margin-bottom:.42rem!important}[data-testid="stChatInput"]{border-radius:14px!important;box-shadow:0 8px 28px rgba(79,70,229,.12)!important}
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden!important;box-shadow:0 6px 20px rgba(37,52,90,.055)}[data-testid="stAlert"]{border-radius:12px!important}
@media(max-width:900px){.block-container{padding-left:.7rem!important;padding-right:.7rem!important}h1{letter-spacing:-1.8px!important}}
</style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "document_ready": False, "interaction_id": None, "document_name": None,
    "document_type": None, "document_bytes": None, "summary": None,
    "messages": [], "active_view": "Summary", "extracted_information": None,
    "extracted_line_items": None, "analysis_result": None,
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

client = get_client()

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
# PRODUCT HEADER
# ============================================================
logo, home, tools, docs, pricing, account = st.columns([2.3, .8, 1.0, 1.15, .8, 1.25], gap="small", vertical_alignment="center")
with logo:
    st.markdown("# ✦ NEXORA")
    st.caption("AI DOCUMENT INTELLIGENCE")
with home: st.caption("Home")
with tools: st.caption("AI Tools")
with docs: st.caption("My Documents")
with pricing: st.caption("Pricing")
with account:
    if logged_in():
        a, b = st.columns([2.4, 1], gap="small")
        with a: st.caption(f"● {display_name()}")
        with b:
            if st.button("↪", help="Log out"): st.logout()
    else:
        if st.button("Login", use_container_width=True):
            if auth_configured():
                st.login()
            else:
                st.info("Login UI is ready. Add the OIDC settings shown below to enable real login.")
st.divider()

# ============================================================
# HOME
# ============================================================
if not st.session_state.document_ready:
    st.markdown("# Your documents. ✦ **Smarter with Nexora.**")
    st.write("Turn complex documents into clear summaries, structured data, intelligent analysis and instant answers.")

    category = st.radio("Nexora tools", ["All", "Understand", "Chat", "Extract", "Analyze"], horizontal=True, label_visibility="collapsed")

    upload_col, feature_col = st.columns([1.55, 1], gap="small", vertical_alignment="top")
    with upload_col:
        with st.container(border=True):
            st.subheader("☁️ Start with a document")
            st.caption("Upload a PDF or image and build your AI workspace.")
            uploaded_file = st.file_uploader("Choose a document", type=["pdf","png","jpg","jpeg"], label_visibility="collapsed", max_upload_size=50)
            if uploaded_file:
                valid, message = validate_file(uploaded_file)
                if not valid:
                    st.error(message)
                else:
                    st.success(f"✓ {uploaded_file.name} is ready")
                    if st.button("✦  Analyze Document", type="primary", use_container_width=True):
                        if process_document(uploaded_file): st.rerun()
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
            ]:
                st.markdown(f"### {icon}  {title}")
                st.caption(text)

    st.subheader("Explore Nexora")
    cards = [
        ("🧠", "AI Summary", "Get the important points without reading every page."),
        ("💬", "Document Chat", "Ask natural-language questions about your document."),
        ("📊", "Extract Data", "Pull names, dates, amounts and line items into tables."),
        ("🔍", "Deep Analysis", "Spot risks, missing information and inconsistencies."),
        ("📄", "Document View", "Keep the original document visible while working."),
        ("⚡", "Quick Insights", "Move from upload to useful information faster."),
    ]
    if category == "Understand": cards = [cards[0], cards[4], cards[5]]
    elif category == "Chat": cards = [cards[1]]
    elif category == "Extract": cards = [cards[2]]
    elif category == "Analyze": cards = [cards[3]]
    for start in range(0, len(cards), 3):
        cols = st.columns(3, gap="small")
        for col, (icon, title, text) in zip(cols, cards[start:start+3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"## {icon}")
                    st.markdown(f"**{title}**")
                    st.caption(text)

    st.write("")
    f1, f2, f3 = st.columns(3, gap="small")
    for col, title, text in [
        (f1, "⚡ Fast", "Optimized AI document workflows."),
        (f2, "🎯 Focused", "Answers based on your uploaded document."),
        (f3, "🔐 Private by design", "Your files stay inside your Nexora workflow."),
    ]:
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(text)

# ============================================================
# WORKSPACE
# ============================================================
else:
    header, new_doc = st.columns([5,1], gap="small", vertical_alignment="center")
    with header:
        st.subheader(f"📄 {st.session_state.document_name}")
        st.caption("● Document analyzed and ready")
    with new_doc:
        if st.button("＋ New document", use_container_width=True):
            reset_workspace(); st.rerun()

    selected = st.radio("Document tools", ["Summary","Extract Data","Analyze"], index=["Summary","Extract Data","Analyze"].index(st.session_state.active_view), horizontal=True, label_visibility="collapsed")
    if selected != st.session_state.active_view:
        st.session_state.active_view = selected; st.rerun()
    st.divider()

    document_column, chat_column = st.columns([1.65,1], gap="small", vertical_alignment="top")
    with document_column:
        with st.container(border=True, height=760):
            st.subheader("📄 Document")
            st.caption(st.session_state.document_name)
            st.divider()
            if st.session_state.document_type == "application/pdf":
                try: st.pdf(st.session_state.document_bytes, height=400)
                except Exception: st.info("PDF preview is unavailable. The document is still available to Nexora.")
            elif st.session_state.document_type and st.session_state.document_type.startswith("image/"):
                st.image(st.session_state.document_bytes, use_container_width=True)
            st.divider()
            if st.session_state.active_view == "Summary":
                st.subheader("✨ AI Summary")
                if st.session_state.summary: st.markdown(st.session_state.summary)
            elif st.session_state.active_view == "Extract Data":
                st.subheader("📊 Extracted Data")
                if st.session_state.extracted_information is None and st.session_state.extracted_line_items is None:
                    st.info("Extract structured information from this document.")
                    if st.button("📊  Extract Data", type="primary", use_container_width=True): extract_data()
                else:
                    info = st.session_state.extracted_information or []
                    items = st.session_state.extracted_line_items or []
                    if info:
                        st.write("**Document Information**"); st.dataframe(pd.DataFrame(info), use_container_width=True, hide_index=True)
                    if items:
                        st.write("**Line Items**"); st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
                    if info or items:
                        st.download_button("⬇️  Download Excel", data=create_excel(), file_name="nexora_extracted_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    else: st.warning("No structured information was found.")
            else:
                st.subheader("🔍 Deep Analysis")
                if not st.session_state.analysis_result:
                    st.info("Run deeper analysis to identify risks, missing information, inconsistencies and next steps.")
                    if st.button("🔍  Run Deep Analysis", type="primary", use_container_width=True): run_deep_analysis()
                else: st.markdown(st.session_state.analysis_result)

    with chat_column:
        with st.container(border=True):
            st.subheader("✦ Nexora AI")
            st.caption("Ask questions and work with your document in real time.")
        with st.container(height=575, border=True):
            if not st.session_state.messages:
                st.info("Ask Nexora anything about this document.")
                st.write("**Try asking:**")
                for suggestion in ["What is this document about?", "What are the most important points?", "Are there any risks I should know about?", "What are the important dates and amounts?", "Summarize this in simple language."]:
                    st.caption(f"• {suggestion}")
            else:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]): st.markdown(message["content"])
        question = st.chat_input("Ask anything about this document...", key="nexora_chat_input")
        if question:
            st.session_state.messages.append({"role":"user","content":question})
            with st.chat_message("user"): st.markdown(question)
            with st.chat_message("assistant"):
                placeholder = st.empty(); answer = ask_document(question, placeholder)
            if answer: st.session_state.messages.append({"role":"assistant","content":answer})
            st.rerun()

st.caption("✦ NEXORA  ·  AI Document Intelligence")
