import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# Stable native Streamlit UI
# ============================================================

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
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background-color: #f8fafc;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

h1 {
    letter-spacing: -1.5px;
}

h2 {
    letter-spacing: -0.8px;
}

h3 {
    letter-spacing: -0.4px;
}

[data-testid="stFileUploader"] {
    background-color: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 16px;
    padding: 10px;
}

.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}

.stDownloadButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}

[data-testid="stChatMessage"] {
    border-radius: 14px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "document_ready" not in st.session_state:
    st.session_state.document_ready = False

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

if "active_page" not in st.session_state:
    st.session_state.active_page = "Summary"


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
# FILE FUNCTIONS
# ============================================================

def get_mime_type(uploaded_file):

    if uploaded_file.type:
        return uploaded_file.type

    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return "application/pdf"

    if name.endswith(".png"):
        return "image/png"

    if name.endswith(".jpg"):
        return "image/jpeg"

    if name.endswith(".jpeg"):
        return "image/jpeg"

    return "application/octet-stream"


def validate_file(uploaded_file):

    mime = get_mime_type(uploaded_file)

    if mime == "application/pdf":

        if uploaded_file.size > MAX_PDF_SIZE:
            return (
                False,
                "This PDF is larger than 50 MB."
            )

    elif mime.startswith("image/"):

        if uploaded_file.size > MAX_IMAGE_SIZE:
            return (
                False,
                "This image is larger than 20 MB."
            )

    else:

        return (
            False,
            "Please upload a PDF, PNG, JPG or JPEG."
        )

    return True, ""


def make_document_part(uploaded_file):

    raw_data = uploaded_file.getvalue()

    encoded_data = base64.b64encode(
        raw_data
    ).decode("utf-8")

    mime_type = get_mime_type(
        uploaded_file
    )

    if mime_type == "application/pdf":

        return {
            "type": "document",
            "data": encoded_data,
            "mime_type": mime_type,
        }

    return {
        "type": "image",
        "data": encoded_data,
        "mime_type": mime_type,
    }


# ============================================================
# RESET
# ============================================================

def reset_workspace():

    st.session_state.document_ready = False
    st.session_state.interaction_id = None
    st.session_state.document_name = None
    st.session_state.document_type = None
    st.session_state.summary = None
    st.session_state.messages = []
    st.session_state.active_page = "Summary"


# ============================================================
# INITIAL DOCUMENT ANALYSIS
# ============================================================

def analyze_document(uploaded_file):

    document_part = make_document_part(
        uploaded_file
    )

    prompt = """
You are Nexora, a professional AI document assistant.

Carefully understand the uploaded document.

Provide the following:

## Executive Summary

Give a clear and concise explanation of what
the document is about.

## Key Information

List the most important information.

Include relevant:
- Names
- Dates
- Amounts
- Organizations
- Reference numbers
- Addresses
- Important terms
- Other critical information

## Important Findings

Explain information that deserves attention.

## Risks and Concerns

Identify possible:
- Risks
- Missing information
- Inconsistencies
- Unusual statements
- Important things the user should verify

If there are no obvious concerns, say so.

## Suggested Questions

Give 5 useful questions the user can ask about
this document.

Rules:

- Do not invent information.
- Use only information contained in the document.
- Preserve dates accurately.
- Preserve numbers accurately.
- If something is unclear, say it is unclear.
- Do not assume missing information.
- Make the answer useful for a normal business user.
"""

    interaction = client.interactions.create(
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

        output_text = getattr(
            interaction,
            "output_text",
            ""
        )

        if not interaction_id:

            st.error(
                "Nexora did not receive a valid response from Gemini."
            )

            return False

        if not output_text:

            st.error(
                "Gemini analyzed the document but returned no text."
            )

            return False

        st.session_state.interaction_id = (
            interaction_id
        )

        st.session_state.summary = (
            output_text
        )

        st.session_state.document_name = (
            uploaded_file.name
        )

        st.session_state.document_type = (
            get_mime_type(uploaded_file)
        )

        st.session_state.document_ready = True

        st.session_state.messages = []

        return True

    except Exception as error:

        error_text = str(error)

        st.error(
            "Nexora could not analyze this document."
        )

        if (
            "500" in error_text
            or "503" in error_text
        ):

            st.warning(
                "Gemini is temporarily busy. "
                "Please try the Analyze Document button again."
            )

        elif "429" in error_text:

            st.warning(
                "The Gemini request limit was reached. "
                "Please wait a little before trying again."
            )

        else:

            st.warning(
                "Please try again. Your document has not been lost."
            )

        with st.expander(
            "Technical information"
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

        placeholder = st.empty()

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
            "Nexora could not answer your question."
        )

        with st.expander(
            "Technical information"
        ):

            st.code(
                str(error)
            )

        return ""


# ============================================================
# EXTRACT DATA
# ============================================================

def extract_data():

    prompt = """
Extract structured information from the document.

Return ONLY valid JSON.

Use this exact structure:

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
- Use an empty string when unavailable.
- Preserve numbers accurately.
- Preserve dates accurately.
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
                "Nexora could not create structured data."
            )

            return

        data = json.loads(
            match.group()
        )

        document_information = data.get(
            "document_information",
            []
        )

        line_items = data.get(
            "line_items",
            []
        )

        if not document_information and not line_items:

            st.warning(
                "No structured information was found."
            )

            return

        info_df = None
        items_df = None

        if document_information:

            info_df = pd.DataFrame(
                document_information
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

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            if info_df is not None:

                info_df.to_excel(
                    writer,
                    sheet_name="Document Information",
                    index=False
                )

            if items_df is not None:

                items_df.to_excel(
                    writer,
                    sheet_name="Line Items",
                    index=False
                )

        st.download_button(
            label="⬇️ Download Excel",
            data=excel_buffer.getvalue(),
            file_name="nexora_extracted_data.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )

    except Exception as error:

        st.error(
            "Data extraction failed."
        )

        with st.expander(
            "Technical information"
        ):

            st.code(
                str(error)
            )


# ============================================================
# DEEP ANALYSIS
# ============================================================

def deep_analysis():

    prompt = """
Perform a detailed analysis of the uploaded document.

Focus on:

1. Important risks
2. Missing information
3. Important dates
4. Important amounts
5. Unusual clauses or statements
6. Potential inconsistencies
7. Information requiring human attention
8. Practical next steps

Do not invent information.

Clearly distinguish facts found in the document
from observations or recommendations.

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

        result = getattr(
            response,
            "output_text",
            ""
        )

        if result:

            st.markdown(result)

        else:

            st.warning(
                "No analysis was returned."
            )

    except Exception as error:

        st.error(
            "Deep analysis failed."
        )

        with st.expander(
            "Technical information"
        ):

            st.code(
                str(error)
            )


# ============================================================
# HEADER
# ============================================================

st.title("✦ NEXORA")

st.caption(
    "Talk to your documents. Understand them. Ask questions. Extract information."
)


# ============================================================
# HOME
# ============================================================

if not st.session_state.document_ready:

    st.markdown(
        "# Talk to your documents."
    )

    st.markdown(
        """
Upload a document and let Nexora help you understand it,
summarize it, ask questions about it, and extract useful data.
"""
    )

    st.divider()

    st.subheader(
        "Upload your document"
    )

    st.caption(
        "Supported formats: PDF, PNG, JPG and JPEG"
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg"
        ],
        label_visibility="visible"
    )

    if uploaded_file:

        valid, message = validate_file(
            uploaded_file
        )

        if not valid:

            st.error(message)

        else:

            st.success(
                f"Document selected: {uploaded_file.name}"
            )

            st.caption(
                f"Size: {uploaded_file.size / (1024 * 1024):.2f} MB"
            )

            st.write("")

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

    st.divider()

    st.subheader(
        "What Nexora can do"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.info(
            """
**🧠 Chat**

Ask questions about
your document.
"""
        )

    with col2:

        st.info(
            """
**⚡ Summarize**

Understand the
important points quickly.
"""
        )

    with col3:

        st.info(
            """
**📊 Extract**

Turn document information
into structured data.
"""
        )

    with col4:

        st.info(
            """
**🔍 Analyze**

Find risks, dates,
amounts and concerns.
"""
        )


# ============================================================
# WORKSPACE
# ============================================================

else:

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.title(
            "Nexora"
        )

        st.caption(
            "Document Workspace"
        )

        st.divider()

        st.markdown(
            "**Current document**"
        )

        st.write(
            st.session_state.document_name
        )

        st.divider()

        selected_page = st.radio(
            "Workspace",
            [
                "Summary",
                "Chat",
                "Extract Data",
                "Analyze",
            ],
            index=[
                "Summary",
                "Chat",
                "Extract Data",
                "Analyze",
            ].index(
                st.session_state.active_page
            ),
        )

        st.session_state.active_page = (
            selected_page
        )

        st.divider()

        if st.button(
            "＋ New Document",
            use_container_width=True
        ):

            reset_workspace()
            st.rerun()


    # --------------------------------------------------------
    # DOCUMENT HEADER
    # --------------------------------------------------------

    st.subheader(
        f"📄 {st.session_state.document_name}"
    )

    st.success(
        "Document ready — Nexora understands this document."
    )

    st.divider()


    # ========================================================
    # SUMMARY
    # ========================================================

    if st.session_state.active_page == "Summary":

        st.header(
            "✨ Document Summary"
        )

        if st.session_state.summary:

            st.markdown(
                st.session_state.summary
            )

        st.divider()

        st.subheader(
            "Continue with your document"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "💬 Chat with Document",
                use_container_width=True
            ):

                st.session_state.active_page = "Chat"
                st.rerun()

        with col2:

            if st.button(
                "📊 Extract Data",
                use_container_width=True
            ):

                st.session_state.active_page = "Extract Data"
                st.rerun()

        with col3:

            if st.button(
                "🔍 Analyze",
                use_container_width=True
            ):

                st.session_state.active_page = "Analyze"
                st.rerun()


    # ========================================================
    # CHAT
    # ========================================================

    elif st.session_state.active_page == "Chat":

        st.header(
            "💬 Chat with your document"
        )

        st.caption(
            "Ask Nexora anything about the uploaded document."
        )

        if not st.session_state.messages:

            st.info(
                "Try asking: "
                "What is this document about?"
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

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    question
                )

            with st.chat_message(
                "assistant"
            ):

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

    elif st.session_state.active_page == "Extract Data":

        st.header(
            "📊 Extract Structured Data"
        )

        st.write(
            "Extract useful information from the document "
            "and download it as Excel."
        )

        st.divider()

        if st.button(
            "📊 Extract Data",
            type="primary",
            use_container_width=True
        ):

            extract_data()


    # ========================================================
    # ANALYZE
    # ========================================================

    elif st.session_state.active_page == "Analyze":

        st.header(
            "🔍 Deep Document Analysis"
        )

        st.write(
            "Nexora will look for risks, missing information, "
            "important dates, amounts, unusual clauses and inconsistencies."
        )

        st.divider()

        if st.button(
            "🔍 Run Deep Analysis",
            type="primary",
            use_container_width=True
        ):

            deep_analysis()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "NEXORA · AI Document Workspace"
)
