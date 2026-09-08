import base64
import io
import json
import re
import time

import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# ============================================================

APP_NAME = "NEXORA"
APP_TAGLINE = "Talk to your documents."

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
# CUSTOM CSS
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


/* ---------- TOP BRAND ---------- */

.nexora-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 30px;
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
    letter-spacing: -0.5px;
}

.nexora-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 1px;
}


/* ---------- HERO ---------- */

.hero {
    text-align: center;
    padding: 34px 20px 30px 20px;
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


/* ---------- UPLOAD CARD ---------- */

.upload-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 28px;
    box-shadow:
        0 18px 50px rgba(15, 23, 42, 0.07);
    margin: 10px auto 30px auto;
}

.upload-title {
    text-align: center;
    font-size: 18px;
    font-weight: 750;
    color: #0f172a;
    margin-bottom: 4px;
}

.upload-description {
    text-align: center;
    color: #64748b;
    font-size: 14px;
    margin-bottom: 20px;
}


/* ---------- FEATURE CARDS ---------- */

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


/* ---------- WORKSPACE ---------- */

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


/* ---------- AI CARD ---------- */

.ai-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
}

.ai-card h3 {
    margin-top: 0;
    color: #0f172a;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}


/* ---------- BUTTONS ---------- */

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


/* ---------- CHAT ---------- */

[data-testid="stChatMessage"] {
    border-radius: 14px;
}


/* ---------- FOOTER ---------- */

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

DEFAULT_STATE = {
    "interaction_id": None,
    "document_name": None,
    "document_type": None,
    "summary": None,
    "messages": [],
    "processed_signature": None,
    "document_ready": False,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error(
            "GEMINI_API_KEY is missing from Streamlit Secrets. "
            "Please add it under Settings → Secrets."
        )
        st.stop()

    return genai.Client(api_key=api_key)


client = get_client()


# ============================================================
# HELPERS
# ============================================================

def reset_document_state():
    st.session_state.interaction_id = None
    st.session_state.document_name = None
    st.session_state.document_type = None
    st.session_state.summary = None
    st.session_state.messages = []
    st.session_state.processed_signature = None
    st.session_state.document_ready = False


def get_file_signature(uploaded_file):
    return f"{uploaded_file.name}:{uploaded_file.size}"


def get_mime_type(uploaded_file):
    mime = uploaded_file.type

    if mime:
        return mime

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
    size = uploaded_file.size

    if mime == "application/pdf":
        if size > MAX_PDF_SIZE:
            return False, "PDF files must be 50 MB or smaller."

    elif mime.startswith("image/"):
        if size > MAX_IMAGE_SIZE:
            return False, "Image files must be 20 MB or smaller."

    else:
        return (
            False,
            "Please upload a PDF, PNG, JPG, or JPEG document.",
        )

    return True, ""


def document_input(uploaded_file):
    raw = uploaded_file.getvalue()
    encoded = base64.b64encode(raw).decode("utf-8")
    mime_type = get_mime_type(uploaded_file)

    if mime_type == "application/pdf":
        content_type = "document"
    else:
        content_type = "image"

    return {
        "type": content_type,
        "data": encoded,
        "mime_type": mime_type,
    }


# ============================================================
# INITIAL DOCUMENT ANALYSIS
# ============================================================

def create_document_interaction(uploaded_file):

    document = document_input(uploaded_file)

    prompt = """
You are Nexora, a professional AI document assistant.

Analyze the uploaded document carefully.

Your job is to understand the document, not merely extract text.

Return a useful professional response containing:

1. A short executive summary.
2. The most important points.
3. Important names, dates, amounts, organizations,
   reference numbers, or other critical information.
4. Important warnings, risks, unusual information,
   missing information, or inconsistencies if present.
5. A list of 5 useful questions a user could ask about
   this document.

Rules:
- Do not invent information.
- If something is unclear, say so.
- Use information actually present in the document.
- Preserve important numbers and dates accurately.
- Keep the response easy to read.
- Use Markdown headings and bullet points.
"""

    interaction = client.interactions.create(
        model=MODEL,
        input=[
            {
                "type": "text",
                "text": prompt,
            },
            document,
        ],
        store=True,
        generation_config={
            "thinking_level": "minimal"
        },
    )

    return interaction


# ============================================================
# CHAT STREAM
# ============================================================

def stream_chat(question, placeholder):

    if not st.session_state.interaction_id:
        return ""

    try:
        stream = client.interactions.create(
            model=MODEL,
            previous_interaction_id=st.session_state.interaction_id,
            input=question,
            store=True,
            stream=True,
            generation_config={
                "thinking_level": "minimal"
            },
        )

        full_text = ""
        completed_id = None

        for event in stream:

            event_type = getattr(
                event,
                "event_type",
                None,
            )

            if event_type == "step.delta":

                delta = getattr(
                    event,
                    "delta",
                    None,
                )

                if delta is not None:

                    delta_type = getattr(
                        delta,
                        "type",
                        None,
                    )

                    if delta_type == "text":

                        text = getattr(
                            delta,
                            "text",
                            "",
                        )

                        if text:
                            full_text += text
                            placeholder.markdown(full_text)

            elif event_type == "interaction.complete":

                completed_id = getattr(
                    event,
                    "id",
                    None,
                )

        if completed_id:
            st.session_state.interaction_id = completed_id

        return full_text

    except Exception as exc:

        error_text = str(exc)

        if "500" in error_text or "503" in error_text:
            placeholder.error(
                "Gemini is temporarily busy. Please try again in a few seconds."
            )
        else:
            placeholder.error(
                f"Unable to process the request: {error_text}"
            )

        return ""


# ============================================================
# DOCUMENT PROCESSING
# ============================================================

def process_document(uploaded_file):

    with st.status(
        "Nexora is reading your document...",
        expanded=False,
    ) as status:

        try:

            interaction = create_document_interaction(
                uploaded_file
            )

            st.session_state.interaction_id = interaction.id

            output = getattr(
                interaction,
                "output_text",
                "",
            )

            st.session_state.summary = output

            st.session_state.document_name = uploaded_file.name
            st.session_state.document_type = get_mime_type(
                uploaded_file
            )

            st.session_state.document_ready = True

            status.update(
                label="Document ready",
                state="complete",
            )

        except Exception as exc:

            status.update(
                label="Unable to process document",
                state="error",
            )

            st.error(
                "Nexora could not process this document."
            )

            with st.expander("Technical details"):
                st.code(str(exc))

            return False

    return True


# ============================================================
# EXTRACT DATA
# ============================================================

def extract_document_data():

    if not st.session_state.interaction_id:
        st.warning("Please upload a document first.")
        return

    prompt = """
Analyze the document and extract the most useful structured data.

Return ONLY valid JSON.

Use this structure:

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
- Do not invent values.
- If a field is unavailable, use an empty string.
- Keep numbers and dates accurate.
"""

    with st.spinner("Extracting structured data..."):

        try:

            response = client.interactions.create(
                model=MODEL,
                previous_interaction_id=st.session_state.interaction_id,
                input=prompt,
                store=True,
                generation_config={
                    "thinking_level": "minimal"
                },
            )

            text = getattr(
                response,
                "output_text",
                "",
            )

            st.session_state.interaction_id = response.id

            match = re.search(
                r"\{.*\}",
                text,
                re.DOTALL,
            )

            if not match:
                st.error(
                    "Nexora could not create structured data from this document."
                )
                return

            data = json.loads(match.group())

            st.success("Data extracted successfully.")

            information = data.get(
                "document_information",
                [],
            )

            line_items = data.get(
                "line_items",
                [],
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
                    hide_index=True,
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
                    hide_index=True,
                )

                excel_buffer = io.BytesIO()

                with pd.ExcelWriter(
                    excel_buffer,
                    engine="openpyxl",
                ) as writer:

                    if information:
                        info_df.to_excel(
                            writer,
                            sheet_name="Document Information",
                            index=False,
                        )

                    items_df.to_excel(
                        writer,
                        sheet_name="Line Items",
                        index=False,
                    )

                st.download_button(
                    label="Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name="nexora_extracted_data.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                )

        except Exception as exc:

            st.error(
                "Extraction failed."
            )

            with st.expander("Technical details"):
                st.code(str(exc))


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="nexora-brand">
    <div class="nexora-logo">N</div>
    <div>
        <div class="nexora-name">NEXORA</div>
        <div class="nexora-sub">AI Document Workspace</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HOME / UPLOAD
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
        unsafe_allow_html=True,
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
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
<div class="feature-card">
    <div class="feature-icon">🧠</div>
    <div class="feature-title">Chat</div>
    <div class="feature-text">
        Ask questions about your document.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
<div class="feature-card">
    <div class="feature-icon">⚡</div>
    <div class="feature-title">Summarize</div>
    <div class="feature-text">
        Get the important information quickly.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
<div class="feature-card">
    <div class="feature-icon">📊</div>
    <div class="feature-title">Extract</div>
    <div class="feature-text">
        Turn document information into structured data.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
<div class="feature-card">
    <div class="feature-icon">🔍</div>
    <div class="feature-title">Analyze</div>
    <div class="feature-text">
        Find important details, risks and inconsistencies.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    if uploaded_file:

        valid, error_message = validate_file(
            uploaded_file
        )

        if not valid:

            st.error(error_message)

        else:

            signature = get_file_signature(
                uploaded_file
            )

            if (
                st.session_state.processed_signature
                != signature
            ):

                st.session_state.processed_signature = signature

                if st.button(
                    "✨ Analyze Document",
                    type="primary",
                    use_container_width=True,
                ):

                    success = process_document(
                        uploaded_file
                    )

                    if success:
                        st.rerun()


# ============================================================
# DOCUMENT WORKSPACE
# ============================================================

else:

    # ---------- SIDEBAR ----------

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
            unsafe_allow_html=True,
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
        font-size:12px;
        color:#64748b;
    ">
        CURRENT DOCUMENT
    </div>
    <div style="
        font-weight:700;
        color:#0f172a;
        margin-top:5px;
        word-break:break-word;
    ">
        {st.session_state.document_name}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button(
            "🧠 Summary",
            use_container_width=True,
        ):
            st.session_state.active_tab = "Summary"

        if st.button(
            "💬 Chat",
            use_container_width=True,
        ):
            st.session_state.active_tab = "Chat"

        if st.button(
            "📊 Extract Data",
            use_container_width=True,
        ):
            st.session_state.active_tab = "Extract"

        if st.button(
            "🔍 Analyze",
            use_container_width=True,
        ):
            st.session_state.active_tab = "Analyze"

        st.markdown("---")

        if st.button(
            "＋ New Document",
            use_container_width=True,
        ):
            reset_document_state()
            st.rerun()


    # ---------- DEFAULT TAB ----------

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Summary"


    # ---------- WORKSPACE HEADER ----------

    st.markdown(
        f"""
<div class="workspace-header">
    <div class="document-name">
        📄 {st.session_state.document_name}
    </div>
    <div class="document-status">
        ● Document analyzed and ready
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    if st.session_state.active_tab == "Summary":

        st.markdown(
            """
<div class="ai-card">
<h3>✨ Document Summary</h3>
</div>
""",
            unsafe_allow_html=True,
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
                use_container_width=True,
            ):
                st.session_state.active_tab = "Chat"
                st.rerun()

        with c2:
            if st.button(
                "📊 Extract data",
                use_container_width=True,
            ):
                st.session_state.active_tab = "Extract"
                st.rerun()

        with c3:
            if st.button(
                "🔍 Analyze document",
                use_container_width=True,
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
<h3>💬 Chat with your document</h3>
<p style="color:#64748b;">
Ask anything about the document. Nexora will answer
using the document as its primary source.
</p>
</div>
""",
            unsafe_allow_html=True,
        )

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

        user_question = st.chat_input(
            "Ask something about this document..."
        )

        if user_question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_question,
                }
            )

            with st.chat_message("user"):
                st.markdown(
                    user_question
                )

            with st.chat_message("assistant"):

                placeholder = st.empty()

                answer = stream_chat(
                    user_question,
                    placeholder,
                )

                if answer:

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )


    # ========================================================
    # EXTRACT
    # ========================================================

    elif st.session_state.active_tab == "Extract":

        st.markdown(
            """
<div class="ai-card">
<h3>📊 Extract structured data</h3>
<p style="color:#64748b;">
Extract useful information from the document and
download it as Excel.
</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("")

        if st.button(
            "📊 Extract Data",
            type="primary",
            use_container_width=True,
        ):
            extract_document_data()


    # ========================================================
    # ANALYZE
    # ========================================================

    elif st.session_state.active_tab == "Analyze":

        st.markdown(
            """
<div class="ai-card">
<h3>🔍 Analyze document</h3>
<p style="color:#64748b;">
Look for important risks, missing information,
unusual clauses, dates, amounts and inconsistencies.
</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("")

        if st.button(
            "🔍 Run Deep Analysis",
            type="primary",
            use_container_width=True,
        ):

            analysis_prompt = """
Analyze this document carefully.

Focus specifically on:

1. Important risks.
2. Missing information.
3. Important dates.
4. Important amounts.
5. Unusual clauses or statements.
6. Potential inconsistencies.
7. Information that deserves human attention.
8. Practical next steps.

Do not invent anything.
Clearly distinguish facts from observations.

Return the answer using clear Markdown headings
and bullet points.
"""

            with st.spinner(
                "Analyzing document..."
            ):

                try:

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

                    analysis = getattr(
                        response,
                        "output_text",
                        "",
                    )

                    st.markdown(
                        analysis
                    )

                except Exception as exc:

                    st.error(
                        "Analysis failed."
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
    unsafe_allow_html=True,
)
