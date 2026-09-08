import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# Professional document workspace
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
    initial_sidebar_state="collapsed",
)


# ============================================================
# PROFESSIONAL THEME
# ============================================================

st.markdown(
    """
<style>

:root {
    --nx-blue: #2563eb;
    --nx-blue-dark: #1d4ed8;
    --nx-purple: #6d28d9;
    --nx-text: #172033;
    --nx-muted: #667085;
    --nx-border: #e4e7ec;
    --nx-bg: #f7f8fa;
    --nx-card: #ffffff;
}


/* PAGE */

.stApp {
    background: var(--nx-bg);
    color: var(--nx-text);
}

.block-container {
    max-width: 1320px;
    padding-top: 1.1rem;
    padding-bottom: 2rem;
}


/* REDUCE DEFAULT SPACING */

.element-container {
    margin-bottom: 0.15rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.45rem;
}


/* TOP BAR */

[data-testid="stHeader"] {
    background: transparent;
}

.nx-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0 12px 0;
    border-bottom: 1px solid var(--nx-border);
    margin-bottom: 12px;
}

.nx-brand {
    display: flex;
    align-items: center;
    gap: 9px;
}

.nx-logo {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: linear-gradient(
        135deg,
        #111827,
        #2563eb
    );
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 800;
}

.nx-name {
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #101828;
}

.nx-tag {
    font-size: 11px;
    color: #98a2b3;
}


/* HOME HERO */

.nx-hero {
    text-align: center;
    padding: 55px 20px 25px 20px;
}

.nx-hero-title {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: -2px;
    color: #101828;
    line-height: 1.05;
}

.nx-hero-gradient {
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nx-hero-sub {
    max-width: 650px;
    margin: 12px auto 0 auto;
    color: #667085;
    font-size: 17px;
    line-height: 1.5;
}


/* CARDS */

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--nx-border);
    border-radius: 14px;
    background: white;
}


/* UPLOAD AREA */

[data-testid="stFileUploader"] {
    background: white;
    border: 1px solid var(--nx-border);
    border-radius: 14px;
    padding: 8px;
}


/* BUTTONS */

.stButton > button {
    border-radius: 8px;
    min-height: 38px;
    font-weight: 650;
    border-color: #d0d5dd;
}

.stButton > button[kind="primary"] {
    background: var(--nx-blue);
    border-color: var(--nx-blue);
}

.stButton > button[kind="primary"]:hover {
    background: var(--nx-blue-dark);
}


/* DOWNLOAD */

.stDownloadButton > button {
    border-radius: 8px;
    min-height: 38px;
    font-weight: 650;
}


/* DOCUMENT WORKSPACE */

.nx-section-title {
    font-size: 15px;
    font-weight: 750;
    color: #344054;
}

.nx-file-title {
    font-size: 16px;
    font-weight: 750;
    color: #101828;
}

.nx-status {
    font-size: 12px;
    color: #12b76a;
    font-weight: 600;
}


/* CHAT */

.nx-chat-title {
    font-size: 16px;
    font-weight: 750;
    color: #101828;
}

.nx-chat-sub {
    font-size: 12px;
    color: #667085;
}


/* FEATURE */

.nx-feature-title {
    font-weight: 700;
    font-size: 14px;
    color: #101828;
}

.nx-feature-text {
    font-size: 12px;
    color: #667085;
    line-height: 1.45;
}


/* MOBILE */

@media (max-width: 800px) {

    .nx-hero-title {
        font-size: 36px;
    }

    .nx-hero {
        padding-top: 30px;
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

        st.session_state[key] = value


# ============================================================
# GEMINI
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
# INITIAL AI ANALYSIS
# ============================================================

def analyze_document(file):

    document_part = make_document_part(file)

    prompt = """
You are Nexora, a professional AI document assistant.

Read and understand the uploaded document.

Create a highly useful document overview.

Return:

## Executive Summary

A concise explanation of what this document is about.

## Key Information

List the most important facts.

Include important:
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

Give 5 useful questions the user can ask about this document.

Rules:
- Do not invent information.
- Use only information present in the document.
- Preserve dates accurately.
- Preserve numbers accurately.
- If something is unclear, say so.
- Keep the result professional and easy to scan.
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

        elif (
            "500" in text
            or "503" in text
        ):

            st.warning(
                "Gemini is temporarily busy. "
                "Please click Analyze Document again."
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

def ask_document(question, placeholder):

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

            st.code(
                str(error)
            )

        return ""


# ============================================================
# EXTRACT STRUCTURED DATA
# ============================================================

def extract_data():

    prompt = """
Extract structured information from the document.

Return ONLY valid JSON.

Use:

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
- Extract only information present.
- Never invent information.
- Use empty strings if unavailable.
- Preserve dates.
- Preserve numbers.
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

            st.code(
                str(error)
            )


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

        st.session_state.analysis_result = getattr(
            response,
            "output_text",
            ""
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

            st.code(
                str(error)
            )


# ============================================================
# DOWNLOAD EXCEL
# ============================================================

def create_excel():

    info = st.session_state.extracted_information or []

    items = st.session_state.extracted_line_items or []

    info_df = pd.DataFrame(info)

    items_df = pd.DataFrame(items)

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
# TOP BRAND
# ============================================================

st.markdown(
    """
<div class="nx-top">

    <div class="nx-brand">

        <div class="nx-logo">
            N
        </div>

        <div>

            <div class="nx-name">
                NEXORA
            </div>

            <div class="nx-tag">
                AI Document Workspace
            </div>

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
<div class="nx-hero">

    <div class="nx-hero-title">
        Talk to your
        <span class="nx-hero-gradient">
            documents.
        </span>
    </div>

    <div class="nx-hero-sub">
        Upload a document and let Nexora summarize,
        analyze, extract data and answer your questions.
    </div>

</div>
""",
        unsafe_allow_html=True
    )

    with st.container(
        border=True
    ):

        st.subheader(
            "Upload your document"
        )

        st.caption(
            "PDF, PNG, JPG or JPEG · Up to 50 MB"
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

                st.error(message)

            else:

                st.success(
                    f"Ready: {uploaded_file.name}"
                )

                if st.button(
                    "✨ Analyze Document",
                    type="primary",
                    use_container_width=True
                ):

                    if process_document(
                        uploaded_file
                    ):

                        st.rerun()

    st.write("")

    col1, col2, col3, col4 = st.columns(
        4,
        gap="small"
    )

    with col1:

        with st.container(border=True):

            st.write("🧠")

            st.markdown(
                "**Chat with documents**"
            )

            st.caption(
                "Ask questions and get answers."
            )

    with col2:

        with st.container(border=True):

            st.write("⚡")

            st.markdown(
                "**AI Summarizer**"
            )

            st.caption(
                "Understand long documents quickly."
            )

    with col3:

        with st.container(border=True):

            st.write("📊")

            st.markdown(
                "**Data extraction**"
            )

            st.caption(
                "Turn documents into structured data."
            )

    with col4:

        with st.container(border=True):

            st.write("🔍")

            st.markdown(
                "**Document analysis**"
            )

            st.caption(
                "Find risks and important details."
            )


# ============================================================
# DOCUMENT WORKSPACE
# ============================================================

else:

    # --------------------------------------------------------
    # COMPACT DOCUMENT HEADER
    # --------------------------------------------------------

    header_left, header_right = st.columns(
        [5, 1],
        gap="small",
        vertical_alignment="center"
    )

    with header_left:

        st.markdown(
            f"### 📄 {st.session_state.document_name}"
        )

        st.caption(
            "● Document analyzed and ready"
        )

    with header_right:

        if st.button(
            "＋ New document",
            use_container_width=True
        ):

            reset_workspace()
            st.rerun()


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # MAIN TWO-PANEL WORKSPACE
    # --------------------------------------------------------

    document_column, chat_column = st.columns(
        [1.65, 1],
        gap="small",
        vertical_alignment="top"
    )


    # ========================================================
    # LEFT — DOCUMENT
    # ========================================================

    with document_column:

        with st.container(
            border=True,
            height=760
        ):

            st.markdown(
                "**📄 DOCUMENT**"
            )

            st.caption(
                st.session_state.document_name
            )

            # ------------------------------------------------
            # PDF / IMAGE VIEWER
            # ------------------------------------------------

            if (
                st.session_state.document_type
                == "application/pdf"
            ):

                try:

                    st.pdf(
                        st.session_state.document_bytes,
                        height=480
                    )

                except Exception:

                    st.info(
                        "PDF preview requires the PDF viewer package."
                    )

            elif (
                st.session_state.document_type
                and st.session_state.document_type.startswith(
                    "image/"
                )
            ):

                st.image(
                    st.session_state.document_bytes,
                    use_container_width=True
                )


            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

            if st.session_state.active_view == "Summary":

                st.divider()

                st.markdown(
                    "#### ✨ AI Summary"
                )

                if st.session_state.summary:

                    st.markdown(
                        st.session_state.summary
                    )


            # ------------------------------------------------
            # EXTRACTED DATA
            # ------------------------------------------------

            elif st.session_state.active_view == "Extract Data":

                st.divider()

                st.markdown(
                    "#### 📊 Extracted Data"
                )

                if (
                    st.session_state.extracted_information
                    is None
                    and st.session_state.extracted_line_items
                    is None
                ):

                    st.info(
                        "Click **Extract Data** below to extract "
                        "structured information from this document."
                    )

                    if st.button(
                        "📊 Extract Data",
                        type="primary",
                        use_container_width=True
                    ):

                        extract_data()

                else:

                    info = (
                        st.session_state.extracted_information
                        or []
                    )

                    items = (
                        st.session_state.extracted_line_items
                        or []
                    )

                    if info:

                        st.markdown(
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

                        st.markdown(
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

                    st.download_button(
                        "⬇️ Download Excel",
                        data=create_excel(),
                        file_name="nexora_extracted_data.xlsx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                        use_container_width=True
                    )


            # ------------------------------------------------
            # ANALYSIS
            # ------------------------------------------------

            elif st.session_state.active_view == "Analyze":

                st.divider()

                st.markdown(
                    "#### 🔍 Deep Analysis"
                )

                if (
                    not st.session_state.analysis_result
                ):

                    st.info(
                        "Run a deeper analysis to identify "
                        "risks, missing information and inconsistencies."
                    )

                    if st.button(
                        "🔍 Run Deep Analysis",
                        type="primary",
                        use_container_width=True
                    ):

                        run_deep_analysis()

                else:

                    st.markdown(
                        st.session_state.analysis_result
                    )


    # ========================================================
    # RIGHT — CHAT
    # ========================================================

    with chat_column:

        with st.container(
            border=True
        ):

            st.markdown(
                "### ✦ Nexora AI"
            )

            st.caption(
                "Ask questions about this document."
            )

        # ----------------------------------------------------
        # CHAT HISTORY
        # ----------------------------------------------------

        chat_history = st.container(
            height=570
        )

        with chat_history:

            if not st.session_state.messages:

                st.info(
                    "Ask Nexora anything about this document."
                )

                st.caption(
                    "Try:"
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

            else:

                for message in st.session_state.messages:

                    with st.chat_message(
                        message["role"]
                    ):

                        st.markdown(
                            message["content"]
                        )


        # ----------------------------------------------------
        # CHAT INPUT
        # ----------------------------------------------------

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

            with chat_history:

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
    "NEXORA · AI Document Workspace"
)
