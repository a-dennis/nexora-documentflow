import io
import time
import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# NEXORA
# Talk to your documents
# ============================================================

MODEL_NAME = "gemini-3.5-flash-lite"

st.set_page_config(
    page_title="Nexora — Talk to Your Documents",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PREMIUM UI
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 50% -10%,
                rgba(70, 90, 255, 0.12),
                transparent 38%
            ),
            #f8f9fc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- HEADER ---------- */

    .nexora-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 3rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 13px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: linear-gradient(
            135deg,
            #111827,
            #374151
        );

        color: white;
        font-size: 22px;
        font-weight: 800;

        box-shadow:
            0 8px 20px rgba(0,0,0,.12);
    }

    .brand-name {
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #111827;
    }

    .brand-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: -2px;
    }

    /* ---------- HERO ---------- */

    .hero {
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 2.5rem;
    }

    .hero h1 {
        font-size: clamp(38px, 5vw, 62px);
        line-height: 1.05;
        letter-spacing: -2.8px;
        font-weight: 850;
        color: #111827;
        margin-bottom: 18px;
    }

    .hero h1 span {
        background: linear-gradient(
            90deg,
            #4f46e5,
            #7c3aed,
            #2563eb
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        max-width: 650px;
        margin: auto;
        color: #6b7280;
        font-size: 18px;
        line-height: 1.6;
    }

    /* ---------- UPLOAD CARD ---------- */

    .upload-card {
        max-width: 760px;
        margin: auto;

        padding: 42px 35px;

        background: rgba(255,255,255,.88);

        border: 1px solid rgba(0,0,0,.07);

        border-radius: 24px;

        box-shadow:
            0 25px 70px rgba(31,41,55,.09);

        text-align: center;
    }

    .upload-icon {
        width: 62px;
        height: 62px;

        margin: 0 auto 18px;

        border-radius: 18px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #eef2ff;

        font-size: 28px;
    }

    .upload-title {
        font-size: 22px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 7px;
    }

    .upload-subtitle {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* ---------- FEATURE CARDS ---------- */

    .features {
        display: grid;
        grid-template-columns:
            repeat(4, 1fr);

        gap: 14px;

        max-width: 900px;

        margin: 30px auto 0;
    }

    .feature {
        padding: 18px;

        background: white;

        border:
            1px solid rgba(0,0,0,.06);

        border-radius: 17px;

        text-align: left;
    }

    .feature-icon {
        font-size: 20px;
        margin-bottom: 10px;
    }

    .feature-title {
        font-size: 14px;
        font-weight: 750;
        color: #111827;
    }

    .feature-text {
        font-size: 12px;
        line-height: 1.5;
        color: #6b7280;
        margin-top: 4px;
    }

    /* ---------- DOCUMENT HEADER ---------- */

    .document-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        background: white;

        border: 1px solid #e5e7eb;

        border-radius: 18px;

        padding: 16px 20px;

        margin-bottom: 18px;
    }

    .document-name {
        font-weight: 750;
        color: #111827;
    }

    .document-meta {
        font-size: 12px;
        color: #6b7280;
        margin-top: 3px;
    }

    /* ---------- SUMMARY ---------- */

    .summary-card {
        background: white;

        border: 1px solid #e5e7eb;

        border-radius: 20px;

        padding: 28px;

        box-shadow:
            0 12px 40px rgba(0,0,0,.04);

        margin-bottom: 20px;
    }

    .section-label {
        font-size: 12px;
        font-weight: 800;

        text-transform: uppercase;

        letter-spacing: .08em;

        color: #6366f1;

        margin-bottom: 10px;
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 11px;
        font-weight: 650;
        min-height: 42px;
    }

    /* ---------- CHAT ---------- */

    [data-testid="stChatMessage"] {
        border-radius: 16px;
        margin-bottom: 10px;
    }

    /* ---------- MOBILE ---------- */

    @media(max-width: 800px) {

        .features {
            grid-template-columns: repeat(2, 1fr);
        }

        .hero h1 {
            letter-spacing: -1.8px;
        }

    }

    @media(max-width: 520px) {

        .features {
            grid-template-columns: 1fr;
        }

        .upload-card {
            padding: 28px 18px;
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
            "GEMINI_API_KEY is missing. "
            "Add it under Streamlit → Settings → Secrets."
        )
        st.stop()

    return genai.Client(api_key=api_key)


client = get_client()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "document_file": None,
    "document_name": None,
    "document_size": None,
    "interaction_id": None,
    "messages": [],
    "summary": None,
    "ready": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def reset_document():

    st.session_state.document_file = None
    st.session_state.document_name = None
    st.session_state.document_size = None
    st.session_state.interaction_id = None
    st.session_state.messages = []
    st.session_state.summary = None
    st.session_state.ready = False


def extract_text_output(interaction):

    try:
        return interaction.output_text
    except Exception:
        pass

    try:

        for output in interaction.outputs:

            if getattr(output, "type", None) == "text":
                return output.text

    except Exception:
        pass

    return ""


def create_document_interaction(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    file_buffer = io.BytesIO(file_bytes)

    gemini_file = client.files.upload(
        file=file_buffer,
        config=types.UploadFileConfig(
            mime_type=uploaded_file.type,
            display_name=uploaded_file.name,
        ),
    )

    # Wait briefly for processing to finish.
    for _ in range(30):

        current = client.files.get(
            name=gemini_file.name
        )

        state = str(
            getattr(current, "state", "")
        ).upper()

        if "ACTIVE" in state:
            gemini_file = current
            break

        if "FAILED" in state:
            raise RuntimeError(
                "Gemini could not process this document."
            )

        time.sleep(0.5)

    prompt = """
You are Nexora, a professional document intelligence assistant.

Analyze the uploaded document carefully.

Return a useful executive summary for the user.

Use exactly these sections:

## SUMMARY

Give a clear concise overview of the document.

## KEY POINTS

Give 5 to 10 important points.

## IMPORTANT INFORMATION

List important:
- dates
- names
- amounts
- deadlines
- obligations
- decisions
- other critical information

Only include information actually present in the document.

## SUGGESTED QUESTIONS

Give 6 useful questions the user could ask about this document.

Do not invent information.
If something is unclear or unavailable, say so.
"""

    interaction = client.interactions.create(

        model=MODEL_NAME,

        store=True,

        input=[
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "document",
                "uri": gemini_file.uri,
                "mime_type": gemini_file.mime_type,
            },
        ],
    )

    return interaction


def ask_document(question):

    interaction = client.interactions.create(

        model=MODEL_NAME,

        store=True,

        previous_interaction_id=(
            st.session_state.interaction_id
        ),

        input=question,
    )

    return interaction


# ============================================================
# HOME / UPLOAD SCREEN
# ============================================================

if not st.session_state.ready:

    st.markdown(
        """
        <div class="nexora-header">

            <div class="brand">

                <div class="brand-mark">
                    N
                </div>

                <div>
                    <div class="brand-name">
                        Nexora
                    </div>

                    <div class="brand-sub">
                        Document Intelligence
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">

            <h1>
                Talk to your
                <span>documents.</span>
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
        <div class="upload-card">

            <div class="upload-icon">
                ↑
            </div>

            <div class="upload-title">
                Drop your PDF here
            </div>

            <div class="upload-subtitle">
                Upload a document and let Nexora understand it.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="features">

            <div class="feature">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">
                    Understand
                </div>
                <div class="feature-text">
                    Get an instant AI summary and key points.
                </div>
            </div>

            <div class="feature">
                <div class="feature-icon">💬</div>
                <div class="feature-title">
                    Ask
                </div>
                <div class="feature-text">
                    Chat naturally with your document.
                </div>
            </div>

            <div class="feature">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">
                    Analyze
                </div>
                <div class="feature-text">
                    Find important dates, risks and information.
                </div>
            </div>

            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-title">
                    Extract
                </div>
                <div class="feature-text">
                    Turn document information into usable data.
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if uploaded_file:

        if uploaded_file.size > 50 * 1024 * 1024:

            st.error(
                "This PDF is larger than 50 MB. "
                "Please upload a smaller document."
            )

        else:

            st.markdown("###")

            if st.button(
                "✦  Analyze document",
                type="primary",
                use_container_width=True,
            ):

                try:

                    with st.spinner(
                        "Nexora is reading your document..."
                    ):

                        interaction = (
                            create_document_interaction(
                                uploaded_file
                            )
                        )

                    summary = extract_text_output(
                        interaction
                    )

                    if not summary:

                        raise RuntimeError(
                            "Nexora received an empty response."
                        )

                    st.session_state.document_file = uploaded_file
                    st.session_state.document_name = (
                        uploaded_file.name
                    )
                    st.session_state.document_size = (
                        uploaded_file.size
                    )
                    st.session_state.interaction_id = (
                        interaction.id
                    )
                    st.session_state.summary = summary
                    st.session_state.ready = True

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not analyze the document: {e}"
                    )


# ============================================================
# DOCUMENT WORKSPACE
# ============================================================

else:

    # ---------- TOP BAR ----------

    st.markdown(
        """
        <div class="nexora-header">

            <div class="brand">

                <div class="brand-mark">
                    N
                </div>

                <div>
                    <div class="brand-name">
                        Nexora
                    </div>

                    <div class="brand-sub">
                        Document Intelligence
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- DOCUMENT INFO ----------

    size_mb = (
        st.session_state.document_size / 1024 / 1024
    )

    st.markdown(
        f"""
        <div class="document-header">

            <div>

                <div class="document-name">
                    📄 {st.session_state.document_name}
                </div>

                <div class="document-meta">
                    {size_mb:.2f} MB · Analyzed by Nexora AI
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- SIDEBAR ----------

    with st.sidebar:

        st.markdown("## Document")

        st.markdown(
            f"**{st.session_state.document_name}**"
        )

        st.divider()

        mode = st.radio(
            "Workspace",
            [
                "🧠 Summary",
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

            reset_document()
            st.rerun()

    # ========================================================
    # SUMMARY
    # ========================================================

    if mode == "🧠 Summary":

        st.markdown(
            """
            <div class="summary-card">

                <div class="section-label">
                    Nexora AI
                </div>

                <h2>
                    Document overview
                </h2>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            st.session_state.summary
        )

        st.divider()

        st.info(
            "Tip: Switch to Chat and ask Nexora anything "
            "about this document."
        )

    # ========================================================
    # CHAT
    # ========================================================

    elif mode == "💬 Chat":

        st.markdown(
            """
            <div class="summary-card">

                <div class="section-label">
                    Document chat
                </div>

                <h2>
                    Ask Nexora anything
                </h2>

                <p>
                    Nexora answers using the uploaded document.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # Existing messages
        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

        question = st.chat_input(
            "Ask anything about this document..."
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

                with st.spinner(
                    "Nexora is thinking..."
                ):

                    try:

                        response = ask_document(
                            question
                        )

                        answer = extract_text_output(
                            response
                        )

                        st.session_state.interaction_id = (
                            response.id
                        )

                        st.markdown(answer)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                    except Exception as e:

                        error_message = (
                            "I couldn't process that question. "
                            f"Please try again.\n\n`{e}`"
                        )

                        st.error(error_message)

    # ========================================================
    # ANALYZE
    # ========================================================

    elif mode == "🔍 Analyze":

        st.markdown(
            """
            <div class="summary-card">

                <div class="section-label">
                    Document analysis
                </div>

                <h2>
                    Find important information
                </h2>

                <p>
                    Ask Nexora to inspect the document
                    for specific information.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        analysis_question = st.text_area(
            "What should Nexora analyze?",
            placeholder=(
                "Example: Find all important dates, "
                "deadlines, financial amounts and potential risks."
            ),
            height=130,
        )

        if st.button(
            "🔍 Analyze",
            type="primary",
            use_container_width=True,
        ):

            if analysis_question.strip():

                with st.spinner(
                    "Analyzing document..."
                ):

                    try:

                        response = ask_document(
                            analysis_question
                        )

                        result = extract_text_output(
                            response
                        )

                        st.session_state.interaction_id = (
                            response.id
                        )

                        st.markdown(result)

                    except Exception as e:

                        st.error(str(e))

            else:

                st.warning(
                    "Tell Nexora what you want to analyze."
                )

    # ========================================================
    # EXTRACT
    # ========================================================

    elif mode == "📊 Extract":

        st.markdown(
            """
            <div class="summary-card">

                <div class="section-label">
                    Data extraction
                </div>

                <h2>
                    Turn document information into data
                </h2>

                <p>
                    This area will become Nexora's
                    PDF → Excel / CSV / JSON workspace.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "The extraction engine from the previous "
            "Nexora version will be connected here next."
        )
