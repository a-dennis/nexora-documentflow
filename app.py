import streamlit as st
import pandas as pd
import json
import os
import tempfile
import re
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nexora DocumentFlow",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 17px;
    color: #666;
    margin-bottom: 25px;
}

.success-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #e9f8ef;
    border: 1px solid #b7e4c7;
}

.info-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #eef5ff;
    border: 1px solid #c7dcff;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">📄 Nexora DocumentFlow</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Turn invoices, PDFs and business documents into clean Excel data automatically.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

if "GEMINI_API_KEY" not in st.secrets:

    st.error(
        "❌ Gemini API key not found.\n\n"
        "Please add GEMINI_API_KEY to Streamlit Secrets."
    )

    st.stop()


try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

except Exception as e:

    st.error(f"❌ Unable to initialize Gemini API: {e}")

    st.stop()


# ============================================================
# MODEL
# ============================================================

# Current low-cost Gemini model optimized for document parsing
MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your document",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Upload an invoice, receipt, purchase order, bill or other business document."
)


# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
You are a highly accurate business-document data extraction system.

Analyze the uploaded document carefully.

Your job is to extract structured information from the document.

IMPORTANT RULES:

1. Do NOT invent information.
2. If a value is not present, return an empty string.
3. Preserve numbers as they appear where possible.
4. Carefully distinguish:
   - Invoice number
   - Invoice date
   - Supplier/vendor
   - Customer/buyer
   - GSTIN
   - Subtotal
   - Tax
   - Total
5. Extract EVERY visible line item.
6. Preserve product/service names accurately.
7. Extract quantity, unit price, tax and line total when available.
8. For Indian GST invoices, carefully identify:
   - CGST
   - SGST
   - IGST
   - GSTIN
9. Do not merge separate line items.
10. Do not create fake line items.
11. If OCR is unclear, use your best interpretation but do not invent values.

Return ONLY valid JSON.

Use exactly this structure:

{
    "document_type": "",
    "document_number": "",
    "date": "",
    "supplier": "",
    "customer": "",
    "supplier_gstin": "",
    "customer_gstin": "",
    "currency": "",
    "subtotal": "",
    "cgst": "",
    "sgst": "",
    "igst": "",
    "tax": "",
    "total": "",
    "line_items": [
        {
            "description": "",
            "quantity": "",
            "unit": "",
            "unit_price": "",
            "tax_rate": "",
            "tax_amount": "",
            "line_total": ""
        }
    ]
}
"""


# ============================================================
# HELPER FUNCTION - CLEAN GEMINI JSON
# ============================================================

def clean_json_response(text):

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fences if Gemini adds them
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # Try extracting the JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:

            possible_json = text[start:end + 1]

            try:
                return json.loads(possible_json)

            except Exception:
                return None

        return None


# ============================================================
# HELPER FUNCTION - NORMALIZE DATA
# ============================================================

def normalize_value(value):

    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return str(value)

    return str(value)


# ============================================================
# PROCESS DOCUMENT
# ============================================================

if uploaded_file is not None:

    st.divider()

    st.subheader("📄 Document")

    col1, col2 = st.columns([2, 1])

    with col1:

        st.write(
            f"**File:** {uploaded_file.name}"
        )

    with col2:

        st.write(
            f"**Size:** {uploaded_file.size / 1024:.1f} KB"
        )


    # --------------------------------------------------------
    # PROCESS BUTTON
    # --------------------------------------------------------

    if st.button(
        "🚀 Extract Data",
        type="primary",
        use_container_width=True
    ):

        temp_path = None
        uploaded_gemini_file = None

        try:

            # ------------------------------------------------
            # SAVE UPLOADED FILE TEMPORARILY
            # ------------------------------------------------

            file_extension = os.path.splitext(
                uploaded_file.name
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=file_extension
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # ------------------------------------------------
            # PROGRESS
            # ------------------------------------------------

            progress = st.progress(0)

            status = st.empty()

            status.info("📤 Uploading document to Gemini...")

            progress.progress(20)


            # ------------------------------------------------
            # UPLOAD TO GEMINI FILES API
            # ------------------------------------------------

            uploaded_gemini_file = client.files.upload(
                file=temp_path
            )

            progress.progress(40)

            status.info(
                "🤖 Gemini is analyzing your document..."
            )


            # ------------------------------------------------
            # GEMINI EXTRACTION
            # ------------------------------------------------

            response = client.models.generate_content(

                model=MODEL_NAME,

                contents=[
                    uploaded_gemini_file,
                    EXTRACTION_PROMPT
                ],

                config={
                    "response_mime_type": "application/json"
                }
            )


            progress.progress(80)

            status.info(
                "📊 Preparing Excel data..."
            )


            # ------------------------------------------------
            # GET RESPONSE
            # ------------------------------------------------

            raw_response = response.text

            extracted_data = clean_json_response(
                raw_response
            )


            if extracted_data is None:

                progress.empty()
                status.empty()

                st.error(
                    "❌ Gemini returned an invalid response. "
                    "Please try the document again."
                )

                with st.expander("Technical response"):

                    st.code(
                        raw_response or "No response received."
                    )

                st.stop()


            # ------------------------------------------------
            # NORMALIZE MAIN FIELDS
            # ------------------------------------------------

            document_type = normalize_value(
                extracted_data.get("document_type")
            )

            document_number = normalize_value(
                extracted_data.get("document_number")
            )

            document_date = normalize_value(
                extracted_data.get("date")
            )

            supplier = normalize_value(
                extracted_data.get("supplier")
            )

            customer = normalize_value(
                extracted_data.get("customer")
            )

            supplier_gstin = normalize_value(
                extracted_data.get("supplier_gstin")
            )

            customer_gstin = normalize_value(
                extracted_data.get("customer_gstin")
            )

            currency = normalize_value(
                extracted_data.get("currency")
            )

            subtotal = normalize_value(
                extracted_data.get("subtotal")
            )

            cgst = normalize_value(
                extracted_data.get("cgst")
            )

            sgst = normalize_value(
                extracted_data.get("sgst")
            )

            igst = normalize_value(
                extracted_data.get("igst")
            )

            tax = normalize_value(
                extracted_data.get("tax")
            )

            total = normalize_value(
                extracted_data.get("total")
            )


            # ------------------------------------------------
            # LINE ITEMS
            # ------------------------------------------------

            line_items = extracted_data.get(
                "line_items",
                []
            )

            if not isinstance(line_items, list):

                line_items = []


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            progress.progress(100)

            status.success(
                "✅ Document processed successfully!"
            )


            # =================================================
            # DISPLAY EXTRACTED INFORMATION
            # =================================================

            st.divider()

            st.subheader("📋 Extracted Information")


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Document Type",
                    document_type or "Not found"
                )

                st.write(
                    "**Document Number**"
                )

                st.write(
                    document_number or "Not found"
                )

                st.write(
                    "**Date**"
                )

                st.write(
                    document_date or "Not found"
                )


            with col2:

                st.write(
                    "**Supplier / Vendor**"
                )

                st.write(
                    supplier or "Not found"
                )

                st.write(
                    "**Supplier GSTIN**"
                )

                st.write(
                    supplier_gstin or "Not found"
                )

                st.write(
                    "**Customer**"
                )

                st.write(
                    customer or "Not found"
                )


            with col3:

                st.write(
                    "**Customer GSTIN**"
                )

                st.write(
                    customer_gstin or "Not found"
                )

                st.write(
                    "**Currency**"
                )

                st.write(
                    currency or "Not found"
                )

                st.write(
                    "**Total**"
                )

                st.write(
                    total or "Not found"
                )


            # =================================================
            # TAX SUMMARY
            # =================================================

            st.subheader("💰 Amount Summary")


            amount_data = pd.DataFrame({

                "Field": [
                    "Subtotal",
                    "CGST",
                    "SGST",
                    "IGST",
                    "Total Tax",
                    "Grand Total"
                ],

                "Value": [
                    subtotal,
                    cgst,
                    sgst,
                    igst,
                    tax,
                    total
                ]

            })


            st.dataframe(
                amount_data,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # LINE ITEMS TABLE
            # =================================================

            st.subheader(
                f"🧾 Line Items ({len(line_items)})"
            )


            if len(line_items) > 0:

                line_item_rows = []

                for item in line_items:

                    if not isinstance(item, dict):
                        continue

                    line_item_rows.append({

                        "Description": normalize_value(
                            item.get("description")
                        ),

                        "Quantity": normalize_value(
                            item.get("quantity")
                        ),

                        "Unit": normalize_value(
                            item.get("unit")
                        ),

                        "Unit Price": normalize_value(
                            item.get("unit_price")
                        ),

                        "Tax Rate": normalize_value(
                            item.get("tax_rate")
                        ),

                        "Tax Amount": normalize_value(
                            item.get("tax_amount")
                        ),

                        "Line Total": normalize_value(
                            item.get("line_total")
                        )

                    })


                if line_item_rows:

                    line_items_df = pd.DataFrame(
                        line_item_rows
                    )

                    st.data_editor(
                        line_items_df,
                        use_container_width=True,
                        num_rows="dynamic"
                    )

                else:

                    line_items_df = pd.DataFrame(
                        columns=[
                            "Description",
                            "Quantity",
                            "Unit",
                            "Unit Price",
                            "Tax Rate",
                            "Tax Amount",
                            "Line Total"
                        ]
                    )

                    st.info(
                        "No line items were detected."
                    )

            else:

                line_items_df = pd.DataFrame(
                    columns=[
                        "Description",
                        "Quantity",
                        "Unit",
                        "Unit Price",
                        "Tax Rate",
                        "Tax Amount",
                        "Line Total"
                    ]
                )

                st.info(
                    "No line items were detected."
                )


            # =================================================
            # CREATE EXCEL FILE
            # =================================================

            summary_df = pd.DataFrame({

                "Field": [
                    "Document Type",
                    "Document Number",
                    "Date",
                    "Supplier",
                    "Customer",
                    "Supplier GSTIN",
                    "Customer GSTIN",
                    "Currency",
                    "Subtotal",
                    "CGST",
                    "SGST",
                    "IGST",
                    "Tax",
                    "Total"
                ],

                "Value": [
                    document_type,
                    document_number,
                    document_date,
                    supplier,
                    customer,
                    supplier_gstin,
                    customer_gstin,
                    currency,
                    subtotal,
                    cgst,
                    sgst,
                    igst,
                    tax,
                    total
                ]

            })


            excel_path = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ).name


            with pd.ExcelWriter(
                excel_path,
                engine="openpyxl"
            ) as writer:

                summary_df.to_excel(
                    writer,
                    sheet_name="Summary",
                    index=False
                )

                line_items_df.to_excel(
                    writer,
                    sheet_name="Line Items",
                    index=False
                )


            # =================================================
            # CSV
            # =================================================

            csv_data = line_items_df.to_csv(
                index=False
            )


            # =================================================
            # DOWNLOAD SECTION
            # =================================================

            st.divider()

            st.subheader(
                "⬇️ Download Results"
            )


            col1, col2 = st.columns(2)


            with open(
                excel_path,
                "rb"
            ) as excel_file:

                excel_bytes = excel_file.read()


            with col1:

                st.download_button(

                    label="📊 Download Excel",

                    data=excel_bytes,

                    file_name=(
                        "nexora_extracted_data.xlsx"
                    ),

                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),

                    use_container_width=True
                )


            with col2:

                st.download_button(

                    label="📄 Download CSV",

                    data=csv_data,

                    file_name=(
                        "nexora_line_items.csv"
                    ),

                    mime="text/csv",

                    use_container_width=True
                )


            # =================================================
            # SUCCESS MESSAGE
            # =================================================

            st.success(
                "🎉 Your document has been successfully converted "
                "into structured data."
            )


            # =================================================
            # DEBUG INFORMATION
            # =================================================

            with st.expander(
                "🔍 View extracted JSON"
            ):

                st.json(
                    extracted_data
                )


            # ------------------------------------------------
            # CLEAN EXCEL TEMP FILE
            # ------------------------------------------------

            try:

                os.remove(
                    excel_path
                )

            except Exception:
                pass


        except Exception as e:

            progress.empty() if "progress" in locals() else None
            status.empty() if "status" in locals() else None

            st.error(
                "❌ Something went wrong while processing "
                "the document."
            )

            st.exception(e)


        finally:

            # ------------------------------------------------
            # CLEAN LOCAL TEMP FILE
            # ------------------------------------------------

            if temp_path:

                try:

                    os.remove(
                        temp_path
                    )

                except Exception:
                    pass


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Nexora DocumentFlow • AI-powered document extraction"
)

st.caption(
    "For testing, use sample or non-confidential documents."
)
