import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# ============================================================

APP_NAME = "NEXORA"
MODEL = "gemini-3.5-flash-lite"

MAX_PDF_SIZE = 50 * 1024 * 1024
MAX_IMAGE_SIZE = 20 * 1024 * 1024


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Nexora — Talk to your documents",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(79, 70, 229, 0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(14, 165, 233, 0.08),
            transparent 28%
        ),
        #f8fafc;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* BRAND */

.nexora-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 28px;
}

.nexora-logo {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #111827, #2563eb);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 800;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.22);
}

.nexora-name {
    font-size: 20px;
    font-weight: 800;
    color: #111827;
}

.nexora-sub {
    font-size: 12px;
    color: #64748b;
}


/* HERO */

.hero {
    text-align: center;
    padding: 30px 20px 25px;
}

.hero h1 {
    font-size: clamp(34px, 5vw, 58px);
    line-height: 1.05;
    letter-spacing: -2.5px;
    color: #0f172a;
    margin: 0;
    font-weight: 850;
}

.hero h1 span {
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #64748b;
    font-size: 18px;
    margin-top: 15px;
}


/* UPLOAD CARD */

.upload-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 25px;
    box-shadow: 0 18px 50px rgba(15, 23, 42, 0.07);
    margin: 10px auto 25px;
}

.upload-title {
    text-align: center;
    font-size: 18px;
    font-weight: 750;
    color: #0f172a;
}

.upload-description {
    text-align: center;
    color: #64748b;
    font-size: 14px;
    margin-top: 5px;
}


/* FEATURE CARDS */

.feature-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px;
    height: 100%;
    box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
}

.feature-icon {
    font-size: 25px;
    margin-bottom: 7px;
}

.feature-title {
    font-weight: 750;
    color: #0f172a;
    font-size: 15px;
}

.feature-text {
    color: #64748b;
    font-size: 13px;
    line-height: 1.5;
}


/* WORKSPACE */

.workspace-header {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 16px;
}

.document-name {
    font-size: 17px;
    font-weight: 750;
    color: #0f172a;
}

.document-status {
    color: #16a34a;
    font-size: 12px;
    font-weight: 650;
    margin-top: 4px;
}


/* AI CARD */

.ai-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}


/* BUTTONS */

.stButton > button {
    border-radius: 10px;
    border: 1px solid #dbe3ef;
    background: white;
    color: #1e293b;
    font-weight: 650;
    min-height: 42px;
}

.stButton > button:hover {
    border-color: #2563eb;
    color: #2563eb;
}


/* FOOTER */

.nexora-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    margin-top: 50px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None

if "document_type" not in st.session_state:
    st.session_state.document_type = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_ready" not in st.session_state:
    st.session_state.document_ready = False

if "uploaded_signature" not in st.session_state:
    st.session_state.uploaded_signature = None

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Summary"


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_client():

    try:
        api_key = st.secrets["GEMINI_API_KEY"]

    except Exception:
        st.error(
            "GEMINI_API_KEY is missing from Streamlit Secrets."
        )
        st.stop()

    return genai.Client(api_key=api_key)


client = get_client()


# ============================================================
# RESET
# ============================================================

def reset_document():

    st.session_state.interaction_id = None
    st.session_state.document_name = None
    st.session_state.document_type = None
    st.session_state.summary = None
    st.session_state.messages = []
    st.session_state.document_ready = False
    st.session_state.uploaded_signature = None
    st.session_state.active_tab = "Summary"


# ============================================================
# FILE HELPERS
# ============================================================

def get_mime_type(uploaded_file):

    if uploaded_file.type:
        return uploaded_file.type

    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return "application/pdf"

    if name.endswith(".png"):
        return "image/png"

    if name.endswith(".jpg") or name.endswith(".jpeg"):
        return "image/jpeg"

    return "application/octet-stream"


def validate_file(uploaded_file):

    mime = get_mime_type(uploaded_file)

    if mime == "application/pdf":

        if uploaded_file.size > MAX_PDF_SIZE:
            return False, "PDF files must be 50 MB or smaller."

    elif mime.startswith("image/"):

        if uploaded_file.size > MAX_IMAGE_SIZE:
            return False, "Image files must be 20 MB or smaller."

    else:

        return (
            False,
            "Please upload a PDF, PNG, JPG, or JPEG document."
        )

    return True, ""


def get_signature(uploaded_file):

    return (
        uploaded_file.name,
        uploaded_file.size
    )


def make_document_part(uploaded_file):

    raw = uploaded_file.getvalue()

    encoded = base64.b64encode(raw).decode("utf-8")

    mime = get_mime_type(uploaded_file)

    if mime == "application/pdf":

        return {
            "type": "document",
            "data": encoded,
            "mime_type": mime,
        }

    return {
        "type": "image",
        "data": encoded,
        "mime_type": mime,
    }


# ============================================================
# ANALYZE DOCUMENT
# ============================================================

def analyze_document(uploaded_file):

    document_part = make_document_part(
        uploaded_file
    )

    prompt = """
You are Nexora, an intelligent professional document assistant.

Analyze the uploaded document carefully.

Your response must contain:

# Executive Summary

Give a concise explanation of what this document is about.

# Key Information

List the most important information found in the document.

Include important:
- Names
- Dates
- Amounts
- Organizations
- Reference numbers
- Addresses
- Important terms
- Other critical information

# Important Findings

Explain anything that deserves attention.

# Risks or Concerns

Identify possible risks, unusual information,
missing information, inconsistencies, or things
that a person should verify.

If there are no obvious risks, say so.

# Suggested Questions

Give 5 useful questions the user can ask Nexora
about this document.

IMPORTANT RULES:

- Do not invent information.
- Use only information found in the document.
- Preserve numbers accurately.
- Preserve dates accurately.
- If information is unclear, say that it is unclear.
- Do not pretend to know information that is not present.
- Use clean Markdown.
- Make the answer useful to a normal business user.
"""

    interaction = client.interactions.create(
        model=MODEL,
        input=[
            {
                "type": "text",
                "text": prompt
            },
            document_part
        ],
        store=True,
        generation_config={
            "thinking_level": "minimal"
        },
    )

    return interaction


# ============================================================
# PROCESS DOCUMENT
# ============================================================

def process_document(uploaded_file):

    try:

        with st.spinner(
            "Nexora is reading and understanding your document..."
        ):

            interaction = analyze_document(
                uploaded_file
            )

        interaction_id = getattr(
            interaction,
            "id",
            None
        )

        if not interaction_id:

            st.error(
                "Nexora received an unexpected response from Gemini."
            )

            return False

        output = getattr(
            interaction,
            "output_text",
            None
        )

        if not output:

            st.error(
                "Nexora could not generate the document analysis."
            )

            return False

        st.session_state.interaction_id = interaction_id

        st.session_state.summary = output

        st.session_state.document_name = (
            uploaded_file.name
        )

        st.session_state.document_type = (
            get_mime_type(uploaded_file)
        )

        st.session_state.document_ready = True

        st.session_state.messages = []

        return True

    except Exception as exc:

        error_text = str(exc)

        st.error(
            "Nexora could not analyze the document."
        )

        if "500" in error_text or "503" in error_text:

            st.warning(
                "Gemini is temporarily busy. "
                "Please click Analyze Document again."
            )

        elif "429" in error_text:

            st.warning(
                "The Gemini API request limit was reached. "
                "Please wait a little and try again."
            )

        else:

            st.warning(
                "Please try the Analyze Document button again."
            )

        with st.expander(
            "Technical details"
        ):

            st.code(
                error_text
            )

        return False


# ============================================================
# CHAT
# ============================================================

def ask_document(question):

    try:

        stream = client.interactions.create(
            model=MODEL,
            previous_interaction_id=(
                st.session_state.interaction_id
            ),
            input=question,
            store=True,
            stream=True,
            generation_config={
                "thinking_level": "minimal"
            },
        )

        answer = ""

        latest_id = None

        placeholder = st.empty()

        for event in stream:

            event_type = getattr(
                event,
                "event_type",
                None
            )

            if event_type == "step.delta":

                delta = getattr(
                    event,
                    "delta",
                    None
                )

                if delta:

                    delta_type = getattr(
                        delta,
                        "type",
                        None
                    )

                    if delta_type == "text":

                        text = getattr(
                            delta,
                            "text",
                            ""
                        )

                        if text:

                            answer += text

                            placeholder.markdown(
                                answer
                            )

            elif event_type == "interaction.complete":

                latest_id = getattr(
                    event,
                    "id",
                    None
                )

        if latest_id:

            st.session_state.interaction_id = latest_id

        return answer

    except Exception as exc:

        st.error(
            "Nexora could not answer that question."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                str(exc)
            )

        return ""


# ============================================================
# EXTRACT DATA
# ============================================================

def extract_data():

    prompt = """
Extract structured information from this document.

Return ONLY valid JSON.

Use exactly this structure:

{
  "document_information": [
    {
      "field": "field name",
      "value": "value"
    }
  ],
  "line_items": [
    {
      "description": "",
      "quantity": "",
      "unit_price": "",
      "amount": ""
    }
  ]
}

Rules:

- Extract only information actually present.
- Never invent values.
- Use empty strings when information is unavailable.
- Preserve numbers accurately.
- Preserve dates accurately.
"""

    try:

        with st.spinner(
            "Extracting structured data..."
        ):

            response = client.interactions.create(
                model=MODEL,
                previous_interaction_id=(
                    st.session_state.interaction_id
                ),
                input=prompt,
                store=True,
                generation_config={
                    "thinking_level": "minimal"
                },
            )

        st.session_state.interaction_id = (
            response.id
        )

        text = getattr(
            response,
            "output_text",
            ""
        )

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:

            st.error(
                "Nexora could not create structured data."
            )

            return

        data = json.loads(
            match.group()
        )

        information = data.get(
            "document_information",
            []
        )

        line_items = data.get(
            "line_items",
            []
        )

        if information:

            info_df = pd.DataFrame(
                information
            )

            st.subheader(
                "Document Information"
            )

            st.dataframe(
                info_df,
                use_container_width=True,
                hide_index=True
            )

        if line_items:

            items_df = pd.DataFrame(
                line_items
            )

            st.subheader(
                "Line Items"
            )

            st.dataframe(
                items_df,
                use_container_width=True,
                hide_index=True
            )

        if information or line_items:

            excel_buffer = io.BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                if information:

                    info_df.to_excel(
                        writer,
                        sheet_name="Document Information",
                        index=False
                    )

                if line_items:

                    items_df.to_excel(
                        writer,
                        sheet_name="Line Items",
                        index=False
                    )

            st.download_button(
                "⬇️ Download Excel",
                data=excel_buffer.getvalue(),
                file_name="nexora_extracted_data.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

        else:

            st.warning(
                "No structured information was found."
            )

    except Exception as exc:

        st.error(
            "Data extraction failed."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                str(exc)
            )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="nexora-brand">

    <div class="nexora-logo">
        N
    </div>

    <div>

        <div class="nexora-name">
            NEXORA
        </div>

        <div class="nexora-sub">
            AI Document Workspace
        </div>

    </div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# HOME
# ============================================================

if not st.session_state.document_ready:

    st.markdown(
        """
<div class="hero">

    <h1>
        Talk to your <span>documents.</span>
    </h1>

    <p>
        Upload a document. Understand it. Ask questions.
        Extract useful information.
    </p>

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="upload-card">

    <div class="upload-title">
        Upload your document
    </div>

    <div class="upload-description">
        PDF, PNG, JPG or JPEG
    </div>

</div>
""",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg"
        ],
        label_visibility="collapsed"
    )

    if uploaded_file:

        valid, message = validate_file(
            uploaded_file
        )

        if not valid:

            st.error(message)

        else:

            current_signature = get_signature(
                uploaded_file
            )

            # IMPORTANT:
            # We no longer hide the button after
            # remembering the uploaded file.

            if (
                st.session_state.uploaded_signature
                != current_signature
            ):

                st.session_state.uploaded_signature = (
                    current_signature
                )

            st.success(
                f"Document selected: {uploaded_file.name}"
            )

            st.markdown("")

            if st.button(
                "✨ Analyze Document",
                type="primary",
                use_container_width=True
            ):

                success = process_document(
                    uploaded_file
                )

                if success:

                    st.rerun()


    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            """
<div class="feature-card">

    <div class="feature-icon">
        🧠
    </div>

    <div class="feature-title">
        Chat
    </div>

    <div class="feature-text">
        Ask questions about your document.
    </div>

</div>
""",
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
<div class="feature-card">

    <div class="feature-icon">
        ⚡
    </div>

    <div class="feature-title">
        Summarize
    </div>

    <div class="feature-text">
        Understand important information quickly.
    </div>

</div>
""",
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
<div class="feature-card">

    <div class="feature-icon">
        📊
    </div>

    <div class="feature-title">
        Extract
    </div>

    <div class="feature-text">
        Convert useful document information into data.
    </div>

</div>
""",
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            """
<div class="feature-card">

    <div class="feature-icon">
        🔍
    </div>

    <div class="feature-title">
        Analyze
    </div>

    <div class="feature-text">
        Find risks, important details and inconsistencies.
    </div>

</div>
""",
            unsafe_allow_html=True
        )


# ============================================================
# WORKSPACE
# ============================================================

else:

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.markdown(
            """
<div style="
    font-size:18px;
    font-weight:800;
    color:#0f172a;
    margin-bottom:20px;
">
    Nexora Workspace
</div>
""",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
<div style="
    padding:12px;
    background:#f8fafc;
    border-radius:12px;
    border:1px solid #e2e8f0;
    margin-bottom:18px;
">

    <div style="
        font-size:11px;
        color:#64748b;
        font-weight:700;
    ">
        CURRENT DOCUMENT
    </div>

    <div style="
        font-weight:700;
        color:#0f172a;
        margin-top:6px;
        word-break:break-word;
    ">
        {st.session_state.document_name}
    </div>

</div>
""",
            unsafe_allow_html=True
        )

        if st.button(
            "🧠 Summary",
            use_container_width=True
        ):

            st.session_state.active_tab = "Summary"
            st.rerun()

        if st.button(
            "💬 Chat",
            use_container_width=True
        ):

            st.session_state.active_tab = "Chat"
            st.rerun()

        if st.button(
            "📊 Extract Data",
            use_container_width=True
        ):

            st.session_state.active_tab = "Extract"
            st.rerun()

        if st.button(
            "🔍 Analyze",
            use_container_width=True
        ):

            st.session_state.active_tab = "Analyze"
            st.rerun()

        st.markdown("---")

        if st.button(
            "＋ New Document",
            use_container_width=True
        ):

            reset_document()
            st.rerun()


    # --------------------------------------------------------
    # WORKSPACE HEADER
    # --------------------------------------------------------

    st.markdown(
        f"""
<div class="workspace-header">

    <div class="document-name">
        📄 {st.session_state.document_name}
    </div>

    <div class="document-status">
        ● Document ready
    </div>

</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    if st.session_state.active_tab == "Summary":

        st.markdown(
            """
<div class="ai-card">

    <h3>
        ✨ Document Summary
    </h3>

</div>
""",
            unsafe_allow_html=True
        )

        if st.session_state.summary:

            st.markdown(
                st.session_state.summary
            )

        st.markdown("---")

        st.subheader(
            "What would you like to do?"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "💬 Ask questions",
                use_container_width=True
            ):

                st.session_state.active_tab = "Chat"
                st.rerun()

        with c2:

            if st.button(
                "📊 Extract data",
                use_container_width=True
            ):

                st.session_state.active_tab = "Extract"
                st.rerun()

        with c3:

            if st.button(
                "🔍 Analyze document",
                use_container_width=True
            ):

                st.session_state.active_tab = "Analyze"
                st.rerun()


    # ========================================================
    # CHAT
    # ========================================================

    elif st.session_state.active_tab == "Chat":

        st.markdown(
            """
<div class="ai-card">

    <h3>
        💬 Chat with your document
    </h3>

    <p style="color:#64748b;">
        Ask anything about the uploaded document.
        Nexora will use the document as its primary source.
    </p>

</div>
""",
            unsafe_allow_html=True
        )

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

        question = st.chat_input(
            "Ask something about this document..."
        )

        if question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            with st.chat_message("user"):

                st.markdown(
                    question
                )

            with st.chat_message("assistant"):

                answer = ask_document(
                    question
                )

            if answer:

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


    # ========================================================
    # EXTRACT
    # ========================================================

    elif st.session_state.active_tab == "Extract":

        st.markdown(
            """
<div class="ai-card">

    <h3>
        📊 Extract Structured Data
    </h3>

    <p style="color:#64748b;">
        Extract useful information from the document
        and download it as Excel.
    </p>

</div>
""",
            unsafe_allow_html=True
        )

        st.markdown("")

        if st.button(
            "📊 Extract Data",
            type="primary",
            use_container_width=True
        ):

            extract_data()


    # ========================================================
    # ANALYZE
    # ========================================================

    elif st.session_state.active_tab == "Analyze":

        st.markdown(
            """
<div class="ai-card">

    <h3>
        🔍 Analyze Document
    </h3>

    <p style="color:#64748b;">
        Find important risks, missing information,
        unusual clauses, dates, amounts and inconsistencies.
    </p>

</div>
""",
            unsafe_allow_html=True
        )

        st.markdown("")

        if st.button(
            "🔍 Run Deep Analysis",
            type="primary",
            use_container_width=True
        ):

            analysis_prompt = """
Analyze this document carefully.

Focus on:

1. Important risks.
2. Missing information.
3. Important dates.
4. Important amounts.
5. Unusual clauses.
6. Potential inconsistencies.
7. Information requiring human attention.
8. Practical next steps.

Do not invent anything.

Clearly distinguish information actually present
in the document from your observations.

Use clear Markdown headings and bullet points.
"""

            try:

                with st.spinner(
                    "Nexora is analyzing the document..."
                ):

                    response = client.interactions.create(
                        model=MODEL,
                        previous_interaction_id=(
                            st.session_state.interaction_id
                        ),
                        input=analysis_prompt,
                        store=True,
                        generation_config={
                            "thinking_level": "minimal"
                        },
                    )

                st.session_state.interaction_id = (
                    response.id
                )

                result = getattr(
                    response,
                    "output_text",
                    ""
                )

                st.markdown(
                    result
                )

            except Exception as exc:

                st.error(
                    "Deep analysis failed."
                )

                with st.expander(
                    "Technical details"
                ):

                    st.code(
                        str(exc)
                    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="nexora-footer">
    NEXORA · AI Document Workspace
</div>
""",
    unsafe_allow_html=True
)
