import streamlit as st
import pandas as pd
import json
import tempfile
import os
from google import genai


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Nexora DocumentFlow",
    page_icon="📄",
    layout="wide"
)


# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #ffffff;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}

.hero {
    padding: 25px 0 10px 0;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 20px;
    color: #555;
    margin-bottom: 25px;
}

.info-card {
    padding: 18px;
    border-radius: 12px;
    background: #f7f9fc;
    border: 1px solid #e5e7eb;
    margin-bottom: 20px;
}

.small-text {
    color: #666;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-title">📄 Nexora DocumentFlow</div>
    <div class="hero-subtitle">
        Turn invoices, receipts and documents into clean Excel data.
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="info-card">
<b>How it works</b><br><br>
1️⃣ Upload a PDF or image<br>
2️⃣ Nexora analyzes the document<br>
3️⃣ Extracted information appears below<br>
4️⃣ Download the result as Excel or CSV
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CHECK API KEY
# ---------------------------------------------------------

if "GEMINI_API_KEY" not in st.secrets:

    st.error(
        "Gemini API key is not configured. "
        "Please add GEMINI_API_KEY to Streamlit Secrets."
    )

    st.stop()


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ---------------------------------------------------------
# FILE UPLOADER
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your document",
    type=["pdf", "png", "jpg", "jpeg"],
    help="For testing, use a sample invoice or receipt without sensitive personal information."
)


# ---------------------------------------------------------
# PROCESS DOCUMENT
# ---------------------------------------------------------

if uploaded_file is not None:

    st.success(f"File received: {uploaded_file.name}")

    process_button = st.button(
        "🚀 Analyze Document",
        type="primary",
        use_container_width=True
    )

    if process_button:

        try:

            # -------------------------------------------------
            # SAVE UPLOADED FILE TEMPORARILY
            # -------------------------------------------------

            file_extension = os.path.splitext(
                uploaded_file.name
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=file_extension
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = temp_file.name


            # -------------------------------------------------
            # UPLOAD TO GEMINI FILES API
            # -------------------------------------------------

            with st.spinner(
                "Analyzing your document..."
            ):

                gemini_file = client.files.upload(
                    file=temp_path
                )


                # -------------------------------------------------
                # EXTRACTION PROMPT
                # -------------------------------------------------

                prompt = """
You are Nexora DocumentFlow, a document data extraction engine.

Analyze the uploaded document carefully.

Your job is to extract structured business information from it.

Return ONLY valid JSON.

Use this exact structure:

{
    "document_type": "",
    "document_number": "",
    "document_date": "",
    "supplier_name": "",
    "supplier_address": "",
    "customer_name": "",
    "customer_address": "",
    "gst_number": "",
    "subtotal": "",
    "tax_amount": "",
    "total_amount": "",
    "currency": "",
    "line_items": [
        {
            "description": "",
            "quantity": "",
            "unit_price": "",
            "tax": "",
            "amount": ""
        }
    ]
}

IMPORTANT RULES:

1. Do not invent information.
2. If a field does not exist, return an empty string.
3. Preserve numbers as they appear in the document.
4. Extract every visible line item.
5. Carefully distinguish subtotal, tax and final total.
6. If the document is not an invoice, still extract whatever fields are relevant.
7. Put line items inside the line_items array.
8. Return JSON only.
"""


                # -------------------------------------------------
                # GEMINI ANALYSIS
                # -------------------------------------------------

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        gemini_file,
                        prompt
                    ],
                    config={
                        "response_mime_type": "application/json"
                    }
                )


                # -------------------------------------------------
                # PARSE RESPONSE
                # -------------------------------------------------

                raw_text = response.text.strip()

                data = json.loads(raw_text)


            # -------------------------------------------------
            # REMOVE TEMP FILE
            # -------------------------------------------------

            try:
                os.remove(temp_path)
            except:
                pass


            # -------------------------------------------------
            # DISPLAY RESULTS
            # -------------------------------------------------

            st.success(
                "✅ Document analyzed successfully!"
            )

            st.divider()

            st.subheader("📋 Extracted Information")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Document Type**")
                st.write(
                    data.get("document_type", "")
                )

                st.write("**Document Number**")
                st.write(
                    data.get("document_number", "")
                )

                st.write("**Document Date**")
                st.write(
                    data.get("document_date", "")
                )

            with col2:
                st.write("**Supplier**")
                st.write(
                    data.get("supplier_name", "")
                )

                st.write("**Customer**")
                st.write(
                    data.get("customer_name", "")
                )

                st.write("**GST Number**")
                st.write(
                    data.get("gst_number", "")
                )

            with col3:
                st.write("**Subtotal**")
                st.write(
                    data.get("subtotal", "")
                )

                st.write("**Tax**")
                st.write(
                    data.get("tax_amount", "")
                )

                st.write("**Total**")
                st.write(
                    data.get("total_amount", "")
                )


            # -------------------------------------------------
            # LINE ITEMS
            # -------------------------------------------------

            st.divider()

            st.subheader("🧾 Line Items")

            line_items = data.get(
                "line_items",
                []
            )

            if line_items:

                df = pd.DataFrame(
                    line_items
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No line items were detected."
                )

                df = pd.DataFrame()


            # -------------------------------------------------
            # DOWNLOAD FILES
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "⬇️ Download Your Data"
            )

            # Create complete Excel workbook
            excel_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            )

            excel_path = excel_file.name
            excel_file.close()


            with pd.ExcelWriter(
                excel_path,
                engine="openpyxl"
            ) as writer:

                summary = pd.DataFrame([
                    {
                        "Field": "Document Type",
                        "Value": data.get(
                            "document_type", ""
                        )
                    },
                    {
                        "Field": "Document Number",
                        "Value": data.get(
                            "document_number", ""
                        )
                    },
                    {
                        "Field": "Document Date",
                        "Value": data.get(
                            "document_date", ""
                        )
                    },
                    {
                        "Field": "Supplier",
                        "Value": data.get(
                            "supplier_name", ""
                        )
                    },
                    {
                        "Field": "Customer",
                        "Value": data.get(
                            "customer_name", ""
                        )
                    },
                    {
                        "Field": "GST Number",
                        "Value": data.get(
                            "gst_number", ""
                        )
                    },
                    {
                        "Field": "Subtotal",
                        "Value": data.get(
                            "subtotal", ""
                        )
                    },
                    {
                        "Field": "Tax",
                        "Value": data.get(
                            "tax_amount", ""
                        )
                    },
                    {
                        "Field": "Total",
                        "Value": data.get(
                            "total_amount", ""
                        )
                    }
                ])

                summary.to_excel(
                    writer,
                    index=False,
                    sheet_name="Summary"
                )


                if not df.empty:

                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Line Items"
                    )


            with open(
                excel_path,
                "rb"
            ) as f:

                excel_bytes = f.read()


            csv_bytes = (
                df.to_csv(
                    index=False
                ).encode("utf-8")
                if not df.empty
                else b""
            )


            col1, col2 = st.columns(2)

            with col1:

                st.download_button(
                    label="📊 Download Excel",
                    data=excel_bytes,
                    file_name="nexora_document.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )


            with col2:

                if csv_bytes:

                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_bytes,
                        file_name="nexora_line_items.csv",
                        mime="text/csv",
                        use_container_width=True
                    )


            try:
                os.remove(excel_path)
            except:
                pass


        except json.JSONDecodeError:

            st.error(
                "Gemini returned an unexpected format. "
                "Please try the document again."
            )


        except Exception as e:

            st.error(
                "Something went wrong while processing the document."
            )

            st.code(
                str(e)
            )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Nexora DocumentFlow • Early MVP • Built for document-to-data automation"
)
