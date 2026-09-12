import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# PHASE 4 — PROFESSIONAL VISUAL EXPERIENCE
# ============================================================

APP_NAME = "NEXORA"
MODEL = "gemini-3.5-flash-lite"

MAX_PDF_SIZE = 50 * 1024 * 1024
MAX_IMAGE_SIZE = 20 * 1024 * 1024


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Nexora — Talk to your documents",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PROFESSIONAL VISUAL SYSTEM
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   NEXORA COLOR SYSTEM
   ========================================================== */

:root {
    --nx-blue: #2563eb;
    --nx-blue2: #3b82f6;
    --nx-indigo: #4f46e5;
    --nx-purple: #7c3aed;
    --nx-cyan: #0891b2;

    --nx-dark: #111827;
    --nx-text: #172033;
    --nx-muted: #64748b;

    --nx-bg1: #f7faff;
    --nx-bg2: #f3f1ff;
    --nx-bg3: #eef7ff;

    --nx-border: #dce4f0;
    --nx-white: #ffffff;

    --nx-shadow:
        0 8px 30px rgba(37, 99, 235, 0.07);

    --nx-shadow-hover:
        0 12px 35px rgba(79, 70, 229, 0.14);
}


/* ==========================================================
   GLOBAL BACKGROUND
   ========================================================== */

.stApp {
    background:
        radial-gradient(
            circle at 8% 8%,
            rgba(59, 130, 246, 0.13),
            transparent 28%
        ),
        radial-gradient(
            circle at 92% 12%,
            rgba(124, 58, 237, 0.11),
            transparent 30%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(14, 165, 233, 0.08),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            var(--nx-bg1),
            var(--nx-bg2),
            var(--nx-bg3)
        );

    color: var(--nx-text);
}


/* ==========================================================
   MAIN CONTENT — PULL EVERYTHING UP
   ========================================================== */

.block-container {
    max-width: 1460px !important;

    padding-top: 0.15rem !important;
    padding-bottom: 0.8rem !important;

    padding-left: 1.6rem !important;
    padding-right: 1.6rem !important;
}


/* ==========================================================
   REMOVE EXCESSIVE STREAMLIT SPACING
   ========================================================== */

[data-testid="stVerticalBlock"] {
    gap: 0.22rem;
}

.element-container {
    margin-bottom: 0.04rem !important;
}


/* ==========================================================
   HEADER
   ========================================================== */

[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
}


/* ==========================================================
   HEADINGS
   ========================================================== */

h1 {
    font-weight: 850 !important;
    letter-spacing: -2px !important;
    color: #111827 !important;
}

h2 {
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    color: #111827 !important;
}

h3 {
    font-weight: 750 !important;
    color: #172033 !important;
}

h4 {
    font-weight: 700 !important;
}


/* ==========================================================
   DIVIDERS
   ========================================================== */

hr {
    border-color: rgba(148, 163, 184, 0.25) !important;

    margin-top: 0.35rem !important;
    margin-bottom: 0.45rem !important;
}


/* ==========================================================
   PREMIUM CONTAINERS
   ========================================================== */

[data-testid="stVerticalBlockBorderWrapper"] {

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.97),
            rgba(248,250,255,0.96)
        ) !important;

    border: 1px solid rgba(148,163,184,0.22) !important;

    border-radius: 17px !important;

    box-shadow:
        0 7px 28px rgba(30,64,175,0.055),
        inset 0 1px 0 rgba(255,255,255,0.85);

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease;
}


/* ==========================================================
   CONTAINER HOVER EFFECT
   ========================================================== */

[data-testid="stVerticalBlockBorderWrapper"]:hover {

    border-color:
        rgba(79,70,229,0.25) !important;

    box-shadow:
        0 12px 36px rgba(79,70,229,0.10),
        inset 0 1px 0 rgba(255,255,255,0.95);
}


/* ==========================================================
   FILE UPLOADER — PREMIUM GLOW
   ========================================================== */

[data-testid="stFileUploader"] {

    background:
        linear-gradient(
            135deg,
            rgba(239,246,255,0.95),
            rgba(245,243,255,0.95)
        ) !important;

    border:
        1.5px dashed rgba(79,70,229,0.38) !important;

    border-radius: 15px !important;

    padding: 0.45rem !important;

    box-shadow:
        0 0 0 1px rgba(59,130,246,0.04),
        0 8px 25px rgba(79,70,229,0.06);

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease;
}


/* uploader hover */

[data-testid="stFileUploader"]:hover {

    border-color:
        rgba(79,70,229,0.72) !important;

    box-shadow:
        0 0 25px rgba(79,70,229,0.12),
        0 10px 30px rgba(37,99,235,0.08);

    transform: translateY(-1px);
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button,
.stDownloadButton > button {

    border-radius: 10px !important;

    min-height: 39px !important;

    font-weight: 700 !important;

    border:
        1px solid rgba(148,163,184,0.35) !important;

    background:
        rgba(255,255,255,0.88) !important;

    box-shadow:
        0 3px 12px rgba(30,64,175,0.04);

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        border-color 0.15s ease;
}


.stButton > button:hover,
.stDownloadButton > button:hover {

    transform: translateY(-1px);

    border-color:
        rgba(79,70,229,0.45) !important;

    box-shadow:
        0 7px 20px rgba(79,70,229,0.10);
}


/* ==========================================================
   PRIMARY BUTTON — BLUE / INDIGO GRADIENT
   ========================================================== */

.stButton > button[kind="primary"] {

    background:
        linear-gradient(
            100deg,
            #2563eb,
            #4f46e5,
            #7c3aed
        ) !important;

    color: white !important;

    border: none !important;

    box-shadow:
        0 8px 22px rgba(79,70,229,0.24);
}


.stButton > button[kind="primary"]:hover {

    background:
        linear-gradient(
            100deg,
            #1d4ed8,
            #4338ca,
            #6d28d9
        ) !important;

    box-shadow:
        0 11px 28px rgba(79,70,229,0.30);

    transform: translateY(-2px);
}


/* ==========================================================
   RADIO NAVIGATION
   ========================================================== */

div[role="radiogroup"] {

    gap: 0.35rem !important;

    padding: 0.18rem !important;

    background:
        rgba(255,255,255,0.70);

    border:
        1px solid rgba(148,163,184,0.18);

    border-radius: 12px;

    width: fit-content;
}


div[role="radiogroup"] label {

    border-radius: 9px !important;

    padding:
        0.30rem
        0.85rem !important;

    font-weight: 650 !important;
}


/* ==========================================================
   CHAT
   ========================================================== */

[data-testid="stChatMessage"] {

    border-radius: 13px !important;

    margin-bottom: 0.45rem !important;
}


/* ==========================================================
   CHAT INPUT
   ========================================================== */

[data-testid="stChatInput"] {

    border-radius: 13px !important;

    box-shadow:
        0 7px 25px rgba(79,70,229,0.10) !important;
}


/* ==========================================================
   INFO / SUCCESS / WARNING
   ========================================================== */

[data-testid="stAlert"] {

    border-radius: 11px !important;

    border-width: 1px !important;
}


/* ==========================================================
   DATAFRAME
   ========================================================== */

[data-testid="stDataFrame"] {

    border-radius: 11px !important;

    overflow: hidden !important;

    box-shadow:
        0 5px 18px rgba(30,64,175,0.05);
}


/* ==========================================================
   CAPTIONS
   ========================================================== */

[data-testid="stCaptionContainer"] {

    color: var(--nx-muted) !important;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 900px) {

    .block-container {

        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;

        padding-top: 0.1rem !important;
    }

    h1 {
        letter-spacing: -1px !important;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "document_ready": False,
    "interaction_id": None,
    "document_name": None,
    "document_type": None,
    "document_bytes": None,
    "summary": None,
    "messages": [],
    "active_view": "Summary",
    "extracted_information": None,
    "extracted_line_items": None,
    "analysis_result": None,
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:

        if isinstance(value, list):
            st.session_state[key] = []

        else:
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
            "GEMINI_API_KEY is missing from Streamlit Secrets."
        )

        st.stop()

    return genai.Client(
        api_key=api_key
    )


client = get_client()


# ============================================================
# FILE HELPERS
# ============================================================

def get_mime_type(file):

    if file.type:
        return file.type

    name = file.name.lower()

    if name.endswith(".pdf"):
        return "application/pdf"

    if name.endswith(".png"):
        return "image/png"

    if name.endswith(".jpg"):
        return "image/jpeg"

    if name.endswith(".jpeg"):
        return "image/jpeg"

    return "application/octet-stream"


def validate_file(file):

    mime = get_mime_type(file)

    if mime == "application/pdf":

        if file.size > MAX_PDF_SIZE:

            return (
                False,
                "PDF files must be 50 MB or smaller."
            )

    elif mime.startswith("image/"):

        if file.size > MAX_IMAGE_SIZE:

            return (
                False,
                "Images must be 20 MB or smaller."
            )

    else:

        return (
            False,
            "Please upload a PDF, PNG, JPG or JPEG."
        )

    return True, ""


def make_document_part(file):

    raw = file.getvalue()

    encoded = base64.b64encode(
        raw
    ).decode("utf-8")

    mime = get_mime_type(file)

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
# RESET
# ============================================================

def reset_workspace():

    for key, value in DEFAULTS.items():

        if isinstance(value, list):

            st.session_state[key] = []

        else:

            st.session_state[key] = value


# ============================================================
# ANALYZE DOCUMENT
# ============================================================

def analyze_document(file):

    document_part = make_document_part(file)

    prompt = """
You are Nexora, a professional AI document assistant.

Read and understand the uploaded document carefully.

Create a useful, accurate and easy-to-read document overview.

Return:

## Executive Summary

Give a concise explanation of what the document is about.

## Key Information

List the most important facts.

Include important information such as:

- Names
- Dates
- Amounts
- Organizations
- Reference numbers
- Addresses
- Important terms
- Other critical information

## Key Takeaways

Give the most useful points a person should know.

## Risks and Concerns

Identify:

- Missing information
- Potential risks
- Inconsistencies
- Unusual clauses
- Important items requiring verification

If none are obvious, clearly say so.

## Suggested Questions

Give 5 useful questions the user could ask about this document.

Rules:

- Do not invent information.
- Use only information present in the document.
- Preserve dates accurately.
- Preserve numbers accurately.
- If something is unclear, say so.
- Keep the result professional.
- Make the result easy to scan.
"""

    return client.interactions.create(
        model=MODEL,

        input=[
            {
                "type": "text",
                "text": prompt,
            },
            document_part,
        ],

        store=True,

        generation_config={
            "thinking_level": "minimal"
        },
    )


# ============================================================
# PROCESS DOCUMENT
# ============================================================

def process_document(file):

    try:

        with st.spinner(
            "Nexora is understanding your document..."
        ):

            interaction = analyze_document(
                file
            )

        interaction_id = getattr(
            interaction,
            "id",
            None
        )

        output = getattr(
            interaction,
            "output_text",
            ""
        )

        if not interaction_id:

            st.error(
                "Nexora did not receive a valid Gemini response."
            )

            return False

        if not output:

            st.error(
                "Nexora received no analysis from Gemini."
            )

            return False

        st.session_state.interaction_id = (
            interaction_id
        )

        st.session_state.summary = output

        st.session_state.document_name = (
            file.name
        )

        st.session_state.document_type = (
            get_mime_type(file)
        )

        st.session_state.document_bytes = (
            file.getvalue()
        )

        st.session_state.document_ready = True

        st.session_state.messages = []

        st.session_state.extracted_information = None

        st.session_state.extracted_line_items = None

        st.session_state.analysis_result = None

        st.session_state.active_view = "Summary"

        return True

    except Exception as error:

        text = str(error)

        st.error(
            "Nexora could not analyze the document."
        )

        if "429" in text:

            st.warning(
                "The Gemini request limit was reached. "
                "Please wait a little and try again."
            )

        elif "500" in text or "503" in text:

            st.warning(
                "Gemini is temporarily busy. "
                "Please try again."
            )

        else:

            st.warning(
                "Please try the Analyze Document button again."
            )

        with st.expander(
            "Technical details"
        ):

            st.code(text)

        return False


# ============================================================
# CHAT
# ============================================================

def ask_document(
    question,
    placeholder
):

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

            st.session_state.interaction_id = (
                latest_id
            )

        return answer

    except Exception as error:

        st.error(
            "Nexora could not answer the question."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(str(error))

        return ""


# ============================================================
# EXTRACT DATA
# ============================================================

def extract_data():

    prompt = """
Extract structured information from the document.

Return ONLY valid JSON.

Use exactly:

{
  "document_information": [
    {
      "field": "",
      "value": ""
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

- Extract only information present in the document.
- Never invent information.
- Use empty strings when information is unavailable.
- Preserve dates accurately.
- Preserve numbers accurately.
- Return valid JSON only.
"""

    try:

        with st.spinner(
            "Extracting structured information..."
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
                "Nexora could not extract structured data."
            )

            return

        data = json.loads(
            match.group()
        )

        st.session_state.extracted_information = (
            data.get(
                "document_information",
                []
            )
        )

        st.session_state.extracted_line_items = (
            data.get(
                "line_items",
                []
            )
        )

        st.session_state.active_view = (
            "Extract Data"
        )

        st.rerun()

    except Exception as error:

        st.error(
            "Data extraction failed."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(str(error))


# ============================================================
# DEEP ANALYSIS
# ============================================================

def run_deep_analysis():

    prompt = """
Perform a detailed analysis of this document.

Focus on:

1. Important risks
2. Missing information
3. Important dates
4. Important amounts
5. Unusual clauses
6. Potential inconsistencies
7. Information requiring human attention
8. Practical next steps

Do not invent anything.

Clearly distinguish facts from observations.

Use clear headings and bullet points.
"""

    try:

        with st.spinner(
            "Nexora is performing deeper analysis..."
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

        st.session_state.analysis_result = (
            getattr(
                response,
                "output_text",
                ""
            )
        )

        st.session_state.active_view = (
            "Analyze"
        )

        st.rerun()

    except Exception as error:

        st.error(
            "Deep analysis failed."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(str(error))


# ============================================================
# EXCEL
# ============================================================

def create_excel():

    info = (
        st.session_state.extracted_information
        or []
    )

    items = (
        st.session_state.extracted_line_items
        or []
    )

    info_df = pd.DataFrame(info)

    items_df = pd.DataFrame(items)

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ):

        pass

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        if not info_df.empty:

            info_df.to_excel(
                writer,
                sheet_name="Document Information",
                index=False
            )

        if not items_df.empty:

            items_df.to_excel(
                writer,
                sheet_name="Line Items",
                index=False
            )

    return output.getvalue()


# ============================================================
# NEXORA HEADER
# ============================================================

brand_col, status_col = st.columns(
    [5, 1],
    gap="small",
    vertical_alignment="center"
)

with brand_col:

    st.title(
        "✦ NEXORA"
    )

    st.caption(
        "AI Document Workspace  ·  "
        "Understand  ·  Analyze  ·  Extract  ·  Ask"
    )


with status_col:

    if st.session_state.document_ready:

        st.success(
            "● Ready"
        )

    else:

        st.info(
            "✦ AI Workspace"
        )


st.divider()


# ============================================================
# HOME
# ============================================================

if not st.session_state.document_ready:

    hero_col, capability_col = st.columns(
        [1.65, 1],
        gap="small",
        vertical_alignment="top"
    )


    # ========================================================
    # HERO / UPLOAD
    # ========================================================

    with hero_col:

        st.header(
            "Talk to your documents."
        )

        st.subheader(
            "Understand. Analyze. Extract. Ask."
        )

        st.caption(
            "Upload a document and let Nexora turn "
            "complex information into clear, useful answers."
        )

        st.write("")

        with st.container(
            border=True
        ):

            st.subheader(
                "☁️  Upload your document"
            )

            st.caption(
                "Start your Nexora workspace"
            )

            uploaded_file = st.file_uploader(
                "Choose a document",

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

                    st.error(
                        message
                    )

                else:

                    st.success(
                        f"✓ {uploaded_file.name} is ready"
                    )

                    if st.button(
                        "✨  Analyze Document",
                        type="primary",
                        use_container_width=True
                    ):

                        if process_document(
                            uploaded_file
                        ):

                            st.rerun()

            else:

                st.caption(
                    "PDF, PNG, JPG or JPEG  ·  "
                    "Maximum 50 MB"
                )


    # ========================================================
    # CAPABILITIES
    # ========================================================

    with capability_col:

        with st.container(
            border=True
        ):

            st.subheader(
                "✦ What Nexora can do"
            )

            st.write(
                "🧠  **AI Summary**"
            )

            st.caption(
                "Understand long documents quickly."
            )

            st.write(
                "💬  **Document Chat**"
            )

            st.caption(
                "Ask questions directly about your document."
            )

            st.write(
                "📊  **Data Extraction**"
            )

            st.caption(
                "Turn document information into structured data."
            )

            st.write(
                "🔍  **Deep Analysis**"
            )

            st.caption(
                "Find risks, missing information and inconsistencies."
            )


    # ========================================================
    # FEATURE STRIP
    # ========================================================

    st.write("")

    feature_1, feature_2, feature_3, feature_4 = st.columns(
        4,
        gap="small"
    )


    with feature_1:

        with st.container(
            border=True
        ):

            st.write("⚡")

            st.markdown(
                "**Fast understanding**"
            )

            st.caption(
                "Get the important points quickly."
            )


    with feature_2:

        with st.container(
            border=True
        ):

            st.write("🎯")

            st.markdown(
                "**Focused answers**"
            )

            st.caption(
                "Ask instead of searching."
            )


    with feature_3:

        with st.container(
            border=True
        ):

            st.write("📋")

            st.markdown(
                "**Structured data**"
            )

            st.caption(
                "Extract useful fields and information."
            )


    with feature_4:

        with st.container(
            border=True
        ):

            st.write("🔎")

            st.markdown(
                "**Smart analysis**"
            )

            st.caption(
                "Find details that need attention."
            )


# ============================================================
# WORKSPACE
# ============================================================

else:

    # ========================================================
    # DOCUMENT HEADER
    # ========================================================

    document_header, new_document = st.columns(
        [5, 1],
        gap="small",
        vertical_alignment="center"
    )

    with document_header:

        st.subheader(
            f"📄 {st.session_state.document_name}"
        )

        st.caption(
            "● Document analyzed and ready"
        )


    with new_document:

        if st.button(
            "＋ New document",
            use_container_width=True
        ):

            reset_workspace()

            st.rerun()


    # ========================================================
    # TOOL NAVIGATION
    # ========================================================

    selected = st.radio(

        "Document tools",

        [
            "Summary",
            "Extract Data",
            "Analyze"
        ],

        index=[
            "Summary",
            "Extract Data",
            "Analyze"
        ].index(
            st.session_state.active_view
        ),

        horizontal=True,

        label_visibility="collapsed"
    )


    if selected != st.session_state.active_view:

        st.session_state.active_view = selected

        st.rerun()


    st.divider()


    # ========================================================
    # MAIN TWO-COLUMN WORKSPACE
    # ========================================================

    document_column, chat_column = st.columns(
        [1.65, 1],
        gap="small",
        vertical_alignment="top"
    )


    # ========================================================
    # DOCUMENT COLUMN
    # ========================================================

    with document_column:

        with st.container(
            border=True,
            height=760
        ):

            st.subheader(
                "📄 Document"
            )

            st.caption(
                st.session_state.document_name
            )

            st.divider()


            # ------------------------------------------------
            # PDF
            # ------------------------------------------------

            if (
                st.session_state.document_type
                == "application/pdf"
            ):

                try:

                    st.pdf(
                        st.session_state.document_bytes,
                        height=415
                    )

                except Exception:

                    st.info(
                        "PDF preview is unavailable. "
                        "The document is still available to Nexora."
                    )


            # ------------------------------------------------
            # IMAGE
            # ------------------------------------------------

            elif (

                st.session_state.document_type

                and

                st.session_state.document_type.startswith(
                    "image/"
                )

            ):

                st.image(
                    st.session_state.document_bytes,
                    use_container_width=True
                )


            st.divider()


            # =================================================
            # SUMMARY
            # =================================================

            if (
                st.session_state.active_view
                == "Summary"
            ):

                st.subheader(
                    "✨ AI Summary"
                )

                if st.session_state.summary:

                    st.markdown(
                        st.session_state.summary
                    )


            # =================================================
            # EXTRACT DATA
            # =================================================

            elif (
                st.session_state.active_view
                == "Extract Data"
            ):

                st.subheader(
                    "📊 Extracted Data"
                )

                if (

                    st.session_state.extracted_information
                    is None

                    and

                    st.session_state.extracted_line_items
                    is None

                ):

                    st.info(
                        "Extract structured information "
                        "from this document."
                    )

                    if st.button(
                        "📊  Extract Data",
                        type="primary",
                        use_container_width=True
                    ):

                        extract_data()


                else:

                    info = (
                        st.session_state
                        .extracted_information
                        or []
                    )

                    items = (
                        st.session_state
                        .extracted_line_items
                        or []
                    )


                    if info:

                        st.write(
                            "**Document Information**"
                        )

                        info_df = pd.DataFrame(
                            info
                        )

                        st.dataframe(
                            info_df,
                            use_container_width=True,
                            hide_index=True
                        )


                    if items:

                        st.write(
                            "**Line Items**"
                        )

                        items_df = pd.DataFrame(
                            items
                        )

                        st.dataframe(
                            items_df,
                            use_container_width=True,
                            hide_index=True
                        )


                    if info or items:

                        st.download_button(
                            "⬇️  Download Excel",

                            data=create_excel(),

                            file_name=(
                                "nexora_extracted_data.xlsx"
                            ),

                            mime=(
                                "application/"
                                "vnd.openxmlformats-officedocument"
                                ".spreadsheetml.sheet"
                            ),

                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "No structured information was found."
                        )


            # =================================================
            # DEEP ANALYSIS
            # =================================================

            elif (
                st.session_state.active_view
                == "Analyze"
            ):

                st.subheader(
                    "🔍 Deep Analysis"
                )

                if not st.session_state.analysis_result:

                    st.info(
                        "Run deeper analysis to identify "
                        "risks, missing information, "
                        "inconsistencies and next steps."
                    )

                    if st.button(
                        "🔍  Run Deep Analysis",
                        type="primary",
                        use_container_width=True
                    ):

                        run_deep_analysis()


                else:

                    st.markdown(
                        st.session_state.analysis_result
                    )


    # ========================================================
    # CHAT COLUMN
    # ========================================================

    with chat_column:

        with st.container(
            border=True
        ):

            st.subheader(
                "✦ Nexora AI"
            )

            st.caption(
                "Your intelligent assistant for this document."
            )


        with st.container(
            height=570,
            border=True
        ):

            if not st.session_state.messages:

                st.info(
                    "Ask Nexora anything about this document."
                )

                st.write(
                    "**Try asking:**"
                )

                st.caption(
                    "• What is this document about?"
                )

                st.caption(
                    "• What are the most important points?"
                )

                st.caption(
                    "• Are there any risks I should know about?"
                )

                st.caption(
                    "• What are the important dates and amounts?"
                )

                st.caption(
                    "• Summarize this in simple language."
                )


            else:

                for message in (
                    st.session_state.messages
                ):

                    with st.chat_message(
                        message["role"]
                    ):

                        st.markdown(
                            message["content"]
                        )


        # ====================================================
        # CHAT INPUT
        # ====================================================

        question = st.chat_input(
            "Ask anything about this document...",
            key="nexora_chat_input"
        )


        if question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )


            with st.chat_message(
                "user"
            ):

                st.markdown(
                    question
                )


            with st.chat_message(
                "assistant"
            ):

                placeholder = st.empty()

                answer = ask_document(
                    question,
                    placeholder
                )


            if answer:

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "✦ NEXORA  ·  AI Document Workspace"
)
