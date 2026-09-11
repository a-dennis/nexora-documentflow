import base64
import io
import json
import re

import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# NEXORA — TALK TO YOUR DOCUMENTS
# Compact Professional Native Streamlit UI
#
# IMPORTANT:
# Processing logic is intentionally preserved.
# UI/layout is the main change in this version.
# ============================================================

APP_NAME = "NEXORA"
MODEL = "gemini-3.5-flash-lite"

MAX_PDF_SIZE = 50 * 1024 * 1024
MAX_IMAGE_SIZE = 20 * 1024 * 1024


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nexora — Talk to your documents",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
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

    return genai.Client(api_key=api_key)


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
# RESET WORKSPACE
# ============================================================

def reset_workspace():

    for key, value in DEFAULTS.items():

        if isinstance(value, list):

            st.session_state[key] = []

        else:

            st.session_state[key] = value


# ============================================================
# DOCUMENT ANALYSIS
# ============================================================

def analyze_document(file):

    document_part = make_document_part(file)

    prompt = """
You are Nexora, a professional AI document assistant.

Read and understand the uploaded document carefully.

Create a useful, accurate and easy-to-read document overview.

Return the following sections:

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
- Make the response easy to scan.
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

            interaction = analyze_document(file)

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

        with st.expander("Technical details"):

            st.code(text)

        return False


# ============================================================
# DOCUMENT CHAT
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

        with st.expander("Technical details"):

            st.code(str(error))

        return ""


# ============================================================
# EXTRACT STRUCTURED DATA
# ============================================================

def extract_data():

    prompt = """
Extract structured information from the document.

Return ONLY valid JSON.

Use exactly this structure:

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

        st.session_state.interaction_id = response.id

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

        with st.expander("Technical details"):

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

        st.session_state.active_view = "Analyze"

        st.rerun()

    except Exception as error:

        st.error(
            "Deep analysis failed."
        )

        with st.expander("Technical details"):

            st.code(str(error))


# ============================================================
# EXCEL CREATION
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
# TOP HEADER
# ============================================================

brand_column, status_column = st.columns(
    [4, 1],
    gap="small",
    vertical_alignment="center"
)

with brand_column:

    st.title("✦ NEXORA")

    st.caption(
        "AI Document Workspace · "
        "Understand · Analyze · Extract · Ask"
    )

with status_column:

    if not st.session_state.document_ready:

        st.info(
            "AI Document Intelligence"
        )

    else:

        st.success(
            "Document Ready"
        )


st.divider()


# ============================================================
# HOME PAGE
# ============================================================

if not st.session_state.document_ready:

    # --------------------------------------------------------
    # COMPACT HERO + CAPABILITIES
    # --------------------------------------------------------

    hero_column, capability_column = st.columns(
        [1.65, 1],
        gap="small",
        vertical_alignment="top"
    )

    # ========================================================
    # HERO / UPLOAD
    # ========================================================

    with hero_column:

        st.header(
            "Talk to your documents."
        )

        st.subheader(
            "Understand. Analyze. Extract. Ask."
        )

        st.write(
            "Upload a document and Nexora will turn it "
            "into useful information you can understand, "
            "search and question."
        )

        st.write("")

        with st.container(
            border=True
        ):

            st.subheader(
                "📤 Upload your document"
            )

            st.caption(
                "PDF, PNG, JPG or JPEG · Maximum 50 MB"
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
                        f"✓ Ready: {uploaded_file.name}"
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

            else:

                st.caption(
                    "Drag and drop your document here, "
                    "or click Browse to select a file."
                )

    # ========================================================
    # CAPABILITIES
    # ========================================================

    with capability_column:

        with st.container(
            border=True
        ):

            st.subheader(
                "✨ What Nexora can do"
            )

            st.write(
                "🧠 **AI Summary**"
            )

            st.caption(
                "Get the important points without reading "
                "the entire document."
            )

            st.write(
                "💬 **Document Chat**"
            )

            st.caption(
                "Ask questions and get answers from "
                "the document."
            )

            st.write(
                "📊 **Data Extraction**"
            )

            st.caption(
                "Turn document information into structured "
                "data and Excel."
            )

            st.write(
                "🔍 **Deep Analysis**"
            )

            st.caption(
                "Identify risks, missing information, "
                "inconsistencies and important details."
            )

    # --------------------------------------------------------
    # COMPACT FEATURE STRIP
    # --------------------------------------------------------

    st.write("")

    feature_1, feature_2, feature_3, feature_4 = st.columns(
        4,
        gap="small"
    )

    with feature_1:

        with st.container(border=True):

            st.write("⚡")

            st.markdown(
                "**Fast understanding**"
            )

            st.caption(
                "Get a useful overview quickly."
            )

    with feature_2:

        with st.container(border=True):

            st.write("🎯")

            st.markdown(
                "**Focused answers**"
            )

            st.caption(
                "Ask questions instead of searching."
            )

    with feature_3:

        with st.container(border=True):

            st.write("📋")

            st.markdown(
                "**Structured information**"
            )

            st.caption(
                "Extract useful fields and line items."
            )

    with feature_4:

        with st.container(border=True):

            st.write("🔎")

            st.markdown(
                "**Document intelligence**"
            )

            st.caption(
                "Find important details and risks."
            )

    st.write("")

    st.info(
        "Nexora keeps your document and AI tools together "
        "in one focused workspace."
    )


# ============================================================
# DOCUMENT WORKSPACE
# ============================================================

else:

    # --------------------------------------------------------
    # DOCUMENT HEADER
    # --------------------------------------------------------

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

    st.write("")

    # --------------------------------------------------------
    # TOOL NAVIGATION
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
    # DOCUMENT + CHAT
    # --------------------------------------------------------

    document_column, chat_column = st.columns(
        [1.65, 1],
        gap="small",
        vertical_alignment="top"
    )

    # ========================================================
    # DOCUMENT SIDE
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
            # PDF PREVIEW
            # ------------------------------------------------

            if (
                st.session_state.document_type
                == "application/pdf"
            ):

                try:

                    st.pdf(
                        st.session_state.document_bytes,
                        height=430
                    )

                except Exception:

                    st.info(
                        "PDF preview is unavailable. "
                        "The document is still available to Nexora."
                    )

            # ------------------------------------------------
            # IMAGE PREVIEW
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
                        "📊 Extract Data",
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
                            "⬇️ Download Excel",
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
    # CHAT SIDE
    # ========================================================

    with chat_column:

        with st.container(
            border=True
        ):

            st.subheader(
                "✦ Nexora AI"
            )

            st.caption(
                "Ask questions about this document."
            )

        st.write("")

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

            with st.container():

                with st.chat_message("user"):

                    st.markdown(question)

                with st.chat_message("assistant"):

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

st.divider()

st.caption(
    "✦ NEXORA · AI Document Workspace"
)
