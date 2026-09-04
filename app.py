import streamlit as st

st.set_page_config(
    page_title="Nexora DocumentFlow",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Nexora DocumentFlow")
st.subheader("Turn documents into clean Excel data")

st.write(
    "Upload an invoice, receipt, or PDF and we'll help convert "
    "the information into structured data."
)

uploaded_file = st.file_uploader(
    "Upload your document",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file:
    st.success(f"File received: {uploaded_file.name}")

    st.info(
        "Document processing will be added in the next step. "
        "This version is only testing the application."
    )

st.divider()

st.caption("Nexora DocumentFlow • MVP")
