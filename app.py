```python
import base64
import time
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# Fast document chat + clean SaaS UI
# ============================================================

MODEL = "gemini-3.5-flash-lite"
MAX_FILE_SIZE = 50 * 1024 * 1024


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Nexora — Talk to Your Documents",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CLEAN PROFESSIONAL UI
# ============================================================

st.markdown(
    """
    <style>

    /* ==============================
       GLOBAL
       ============================== */

    .stApp {
        background: #f6f7fb;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* ==============================
       BRAND
       ============================== */

    .nx-brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin-bottom: 28px;
    }

    .nx-logo {
        width: 42px;
        height: 42px;
        border-radius: 13px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: linear-gradient(
            135deg,
            #111827,
            #4f46e5
        );

        color: white;
        font-size: 20px;
        font-weight: 800;

        box-shadow:
            0 8px 22px rgba(79,70,229,.22);
    }

    .nx-name {
        font-size: 22px;
        line-height: 1;
        font-weight: 800;
        color: #111827;
    }

    .nx-tagline {
        margin-top: 5px;
        font-size: 11px;
        color: #737780;
    }


    /* ==============================
       HERO
       ============================== */

    .nx-hero {
        text-align: center;
        padding: 35px 10px 25px;
    }

    .nx-hero h1 {
        margin: 0;

        font-size: clamp(
            38px,
            5vw,
            62px
        );

        line-height: 1.04;

        letter-spacing: -2.8px;

        font-weight: 850;

        color: #111827;
    }

    .nx-gradient {
        background: linear-gradient(
            90deg,
            #4f46e5,
            #7c3aed,
            #2563eb
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .nx-hero p {
        max-width: 650px;
        margin: 18px auto 0;

        font-size: 17px;
        line-height: 1.6;

        color: #69707d;
    }


    /* ==============================
       UPLOAD AREA
       ============================== */

    .nx-upload-card {
        max-width: 760px;
        margin: 15px auto 25px;

        padding: 34px;

        background: white;

        border:
            1px solid #e6e8ef;

        border-radius: 22px;

        box-shadow:
            0 18px 50px rgba(17,24,39,.07);
    }

    .nx-upload-icon {
        width: 58px;
        height: 58px;

        margin: 0 auto 15px;

        border-radius: 17px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #eef2ff;

        font-size: 25px;
    }

    .nx-upload-title {
        text-align: center;

        font-size: 21px;
        font-weight: 750;

        color: #111827;
    }

    .nx-upload-text {
        text-align: center;

        margin-top: 6px;

        color: #737780;

        font-size: 13px;
    }


    /* ==============================
       FEATURE CARDS
       ============================== */

    .nx-feature {
        min-height: 125px;

        padding: 18px;

        background: white;

        border:
            1px solid #e7e9ef;

        border-radius: 16px;

        box-shadow:
            0 6px 20px rgba(17,24,39,.035);
    }

    .nx-feature-icon {
        font-size: 21px;
        margin-bottom: 8px;
    }

    .nx-feature-title {
        font-size: 14px;
        font-weight: 750;
        color: #171923;
    }

    .nx-feature-text {
        margin-top: 5px;

        font-size: 12px;
        line-height: 1.45;

        color: #777d89;
    }


    /* ==============================
       WORKSPACE
       ============================== */

    .nx-panel {
        background: white;

        border:
            1px solid #e5e7eb;

        border-radius: 18px;

        padding: 24px;

        box-shadow:
            0 8px 28px rgba(17,24,39,.04);

        margin-bottom: 18px;
    }

    .nx-label {
        font-size: 11px;

        text-transform: uppercase;

        letter-spacing: .09em;

        font-weight: 800;

        color: #6366f1;

        margin-bottom: 7px;
    }

    .nx-title {
        font-size: 25px;

        font-weight: 800;

        color: #111827;

        margin-bottom: 6px;
    }

    .nx-description {
        font-size: 13px;

        color: #717784;
    }


    /* ==============================
       SIDEBAR
       ============================== */

    section[data-testid="stSidebar"] {
        background: white;

        border-right:
            1px solid #e6e8ee;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.4rem;
    }


    /* ==============================
       BUTTONS
       ============================== */

    .stButton > button {
        border-radius: 10px;

        min-height: 42px;

        font-weight: 650;

        border-color: #e1e4eb;
    }


    /* ==============================
       CHAT
       ============================== */

    [data-testid="stChatMessage"] {
        border-radius: 15px;
    }

    [data-testid="stChatInput"] {
        border-radius: 14px;
    }


    /* ==============================
       MOBILE
       ============================== */

    @media (max-width: 700px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .nx-hero h1 {
            font-size: 40px;
            letter-spacing: -1.8px;
        }

        .nx-upload-card {
            padding: 22px 16px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_client():

    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "GEMINI_API_KEY is missing from Streamlit Secrets."
        )
        st.stop()

    return genai.Client(api_key=api_key)


client = get_client()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "document_name": None,
    "document_size": None,
    "interaction_id": None,
    "summary": None,
    "messages": [],
    "document_loaded": False,
    "busy": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# FUNCTIONS
# ============================================================

def reset_app():

    for key, value in defaults.items():
        st.session_state[key] = value


def create_initial_interaction(uploaded_file):

    raw = uploaded_file.getvalue()

    encoded = base64.b64encode(raw).decode("utf-8")

    prompt = """
You are Nexora, a professional document intelligence assistant.

Analyze the uploaded document and give the user a concise,
high-value overview.

Use this structure:

## Overview

Explain what this document is about in 2-4 sentences.

## Key points

Give the 5-8 most important points.

## Important information

Include important dates, names, amounts, deadlines,
obligations, decisions, or other critical information
that are actually present.

## Suggested questions

Give 5 useful questions the user could ask about this
document.

Rules:
- Never invent information.
- If something is not available, say so.
- Be concise.
- Use simple professional language.
"""

    interaction = client.interactions.create(
        model=MODEL,
        input=[
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "document",
                "data": encoded,
                "mime_type": uploaded_file.type,
            },
        ],
        store=True,
        generation_config={
            "thinking_level": "minimal",
        },
    )

    return interaction


def stream_answer(question):

    stream = client.interactions.create(
        model=MODEL,
        previous_interaction_id=(
            st.session_state.interaction_id
        ),
        input=question,
        store=True,
        stream=True,
        generation_config={
            "thinking_level": "minimal",
        },
    )

    answer_parts = []
    final_id = None

    placeholder = st.empty()

    for event in stream:

        # Capture final interaction ID
        if getattr(event, "interaction", None):

            try:
                final_id = event.interaction.id
            except Exception:
                pass

        # Stream text
        if getattr(event, "event_type", None) == "step.delta":

            delta = getattr(event, "delta", None)

            if delta and getattr(
                delta,
                "type",
                None
            ) == "text":

                text = getattr(
                    delta,
                    "text",
                    ""
                )

                if text:

                    answer_parts.append(text)

                    placeholder.markdown(
                        "".join(answer_parts)
                    )

    answer = "".join(answer_parts).strip()

    if final_id:
        st.session_state.interaction_id = final_id

    return answer


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="nx-brand">

        <div class="nx-logo">
            N
        </div>

        <div>
            <div class="nx-name">
                Nexora
            </div>

            <div class="nx-tagline">
                Document Intelligence
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HOME
# ============================================================

if not st.session_state.document_loaded:

    st.markdown(
        """
        <div class="nx-hero">

            <h1>
                Talk to your
                <span class="nx-gradient">
                    documents.
                </span>
            </h1>

            <p>
                Upload a document, understand it instantly,
                and ask questions in plain language.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="nx-upload-card">

            <div class="nx-upload-icon">
                ↑
            </div>

            <div class="nx-upload-title">
                Upload your document
            </div>

            <div class="nx-upload-text">
                PDF up to 50 MB
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    # ----------------------------------------
    # FEATURES
    # ----------------------------------------

    cols = st.columns(4)

    features = [
        (
            "🧠",
            "Understand",
            "Get an AI summary and important points."
        ),
        (
            "💬",
            "Ask",
            "Chat naturally with your document."
        ),
        (
            "🔍",
            "Analyze",
            "Find dates, amounts, clauses and risks."
        ),
        (
            "📊",
            "Extract",
            "Turn document information into useful data."
        ),
    ]

    for col, feature in zip(cols, features):

        icon, title, text = feature

        with col:

            st.markdown(
                f"""
                <div class="nx-feature">

                    <div class="nx-feature-icon">
                        {icon}
                    </div>

                    <div class="nx-feature-title">
                        {title}
                    </div>

                    <div class="nx-feature-text">
                        {text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    # ----------------------------------------
    # PROCESS DOCUMENT
    # ----------------------------------------

    if uploaded_file:

        if uploaded_file.size > MAX_FILE_SIZE:

            st.error(
                "This file is larger than 50 MB. "
                "Please upload a smaller PDF."
            )

        else:

            st.markdown("")

            if st.button(
                "✦  Understand this document",
                type="primary",
                use_container_width=True,
            ):

                try:

                    start = time.time()

                    with st.spinner(
                        "Nexora is reading your document..."
                    ):

                        interaction = (
                            create_initial_interaction(
                                uploaded_file
                            )
                        )

                    elapsed = time.time() - start

                    st.session_state.document_name = (
                        uploaded_file.name
                    )

                    st.session_state.document_size = (
                        uploaded_file.size
                    )

                    st.session_state.interaction_id = (
                        interaction.id
                    )

                    st.session_state.summary = (
                        interaction.output_text
                    )

                    st.session_state.document_loaded = True

                    st.session_state.messages = []

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Nexora could not process this PDF."
                    )

                    st.exception(e)


# ============================================================
# DOCUMENT WORKSPACE
# ============================================================

else:

    # ----------------------------------------
    # SIDEBAR
    # ----------------------------------------

    with st.sidebar:

        st.markdown("### ✦ Nexora")

        st.caption("Your document workspace")

        st.divider()

        st.markdown(
            f"**📄 {st.session_state.document_name}**"
        )

        st.caption(
            f"{st.session_state.document_size / 1024 / 1024:.2f} MB"
        )

        st.divider()

        workspace = st.radio(
            "Workspace",
            [
                "🧠 Overview",
                "💬 Chat",
                "🔍 Analyze",
                "📊 Extract",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        if st.button(
            "＋ New document",
            use_container_width=True,
        ):

            reset_app()
            st.rerun()


    # ----------------------------------------
    # DOCUMENT TOP BAR
    # ----------------------------------------

    st.markdown(
        f"""
        <div class="nx-panel">

            <div class="nx-label">
                CURRENT DOCUMENT
            </div>

            <div class="nx-title">
                📄 {st.session_state.document_name}
            </div>

            <div class="nx-description">
                Nexora has analyzed this document.
                Choose a workspace from the left.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # OVERVIEW
    # ========================================================

    if workspace == "🧠 Overview":

        st.markdown(
            """
            <div class="nx-panel">

                <div class="nx-label">
                    AI OVERVIEW
                </div>

                <div class="nx-title">
                    Document summary
                </div>

                <div class="nx-description">
                    A concise understanding of your document.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            st.session_state.summary
        )

        st.divider()

        st.info(
            "Switch to Chat to ask Nexora questions "
            "about this document."
        )


    # ========================================================
    # CHAT
    # ========================================================

    elif workspace == "💬 Chat":

        st.markdown(
            """
            <div class="nx-panel">

                <div class="nx-label">
                    DOCUMENT CHAT
                </div>

                <div class="nx-title">
                    Ask Nexora anything
                </div>

                <div class="nx-description">
                    Ask questions about the document
                    in normal language.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # Suggested questions
        if not st.session_state.messages:

            st.markdown("**Try asking:**")

            suggestions = [
                "What is this document about?",
                "What are the most important points?",
                "What are the important dates?",
                "Are there any risks or unusual clauses?",
            ]

            suggestion_cols = st.columns(2)

            for i, question in enumerate(suggestions):

                with suggestion_cols[i % 2]:

                    if st.button(
                        question,
                        key=f"suggestion_{i}",
                        use_container_width=True,
                    ):

                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": question,
                            }
                        )

                        st.rerun()


        # Existing chat
        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )


        question = st.chat_input(
            "Ask anything about your document..."
        )


        if question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.chat_message("user"):

                st.markdown(question)


            with st.chat_message("assistant"):

                try:

                    answer = stream_answer(
                        question
                    )

                    if not answer:

                        answer = (
                            "I couldn't generate an answer. "
                            "Please try again."
                        )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as e:

                    st.error(
                        "Nexora encountered a temporary "
                        "problem while answering."
                    )

                    st.caption(str(e))


    # ========================================================
    # ANALYZE
    # ========================================================

    elif workspace == "🔍 Analyze":

        st.markdown(
            """
            <div class="nx-panel">

                <div class="nx-label">
                    ANALYSIS
                </div>

                <div class="nx-title">
                    Analyze your document
                </div>

                <div class="nx-description">
                    Tell Nexora exactly what you want to find.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        analysis = st.text_area(
            "Analysis request",
            placeholder=(
                "Example:\n"
                "Find all important dates, financial amounts "
                "and obligations in this document."
            ),
            height=130,
            label_visibility="collapsed",
        )

        if st.button(
            "🔍 Analyze",
            type="primary",
            use_container_width=True,
        ):

            if not analysis.strip():

                st.warning(
                    "Tell Nexora what you want to analyze."
                )

            else:

                with st.chat_message("assistant"):

                    try:

                        result = stream_answer(
                            analysis
                        )

                        st.markdown(result)

                    except Exception as e:

                        st.error(str(e))


    # ========================================================
    # EXTRACT
    # ========================================================

    elif workspace == "📊 Extract":

        st.markdown(
            """
            <div class="nx-panel">

                <div class="nx-label">
                    DATA EXTRACTION
                </div>

                <div class="nx-title">
                    Extract useful data
                </div>

                <div class="nx-description">
                    Convert information from your document
                    into structured data.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "PDF → Excel / CSV / JSON extraction "
            "will be connected here in the next build."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Nexora · Talk to your documents."
)
```
