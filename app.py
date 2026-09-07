import streamlit as st
import pandas as pd
import json
import os
import tempfile
import time
import re
from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Nexora DocumentFlow",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 4px;
}

.subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 25px;
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
# GEMINI CONFIGURATION
# ============================================================

if "GEMINI_API_KEY" not in st.secrets:

    st.error(
        "❌ GEMINI_API_KEY is missing from Streamlit Secrets."
    )

    st.stop()


try:

    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

except Exception as e:

    st.error(
        f"❌ Could not initialize Gemini: {e}"
    )

    st.stop()


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
You are an expert business-document data extraction system.

Carefully analyze the uploaded document.

Extract ONLY information that is actually visible in the document.

NEVER invent or guess missing information.

If a field does not exist, return an empty string.

Extract EVERY visible line item.

Do not merge different line items.

For Indian invoices, carefully identify:

- Invoice number
- Invoice date
- Supplier/vendor
- Customer/buyer
- Supplier GSTIN
- Customer GSTIN
- HSN/SAC if visible
- Quantity
- Unit
- Unit price
- Tax rate
- CGST
- SGST
- IGST
- Total tax
- Grand total

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
# JSON CLEANER
# ============================================================

def clean_json_response(text):

    if not text:
        return None

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    try:

        return json.loads(text)

    except Exception:

        start = text.find("{")
        end = text.rfind("}")

        if start >= 0 and end > start:

            try:

                return json.loads(
                    text[start:end + 1]
                )

            except Exception:

                return None

        return None


# ============================================================
# SAFE VALUE
# ============================================================

def safe_value(value):

    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return str(value)

    return str(value)


# ============================================================
# WAIT FOR GEMINI FILE
# ============================================================

def wait_for_file_ready(
    uploaded_file,
    status_box,
    progress_bar,
    max_wait=60
):

    start_time = time.time()

    while True:

        try:

            current_file = client.files.get(
                name=uploaded_file.name
            )

        except Exception as e:

            raise Exception(
                f"Unable to check Gemini file status: {e}"
            )


        # Get state safely
        state = getattr(
            current_file,
            "state",
            None
        )

        state_name = getattr(
            state,
            "name",
            str(state)
        )

        state_name = str(
            state_name
        ).upper()


        # ----------------------------------------------------
        # FILE READY
        # ----------------------------------------------------

        if "ACTIVE" in state_name:

            progress_bar.progress(45)

            status_box.success(
                "✅ Document uploaded and ready for analysis."
            )

            return current_file


        # ----------------------------------------------------
        # FILE FAILED
        # ----------------------------------------------------

        if "FAILED" in state_name:

            raise Exception(
                "Gemini could not process this document."
            )


        # ----------------------------------------------------
        # STILL PROCESSING
        # ----------------------------------------------------

        elapsed = int(
            time.time() - start_time
        )

        if elapsed >= max_wait:

            raise Exception(
                "Gemini took too long to process the "
                "uploaded document. Please try again."
            )


        progress = min(
            45,
            25 + int(elapsed / max_wait * 20)
        )

        progress_bar.progress(
            progress
        )

        status_box.info(
            f"⏳ Gemini is processing the document... "
            f"{elapsed}s"
        )

        time.sleep(2)


# ============================================================
# FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your document",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ],
    help=(
        "Upload an invoice, receipt, purchase order, "
        "bill or business document."
    )
)


# ============================================================
# PROCESS DOCUMENT
# ============================================================

if uploaded_file is not None:

    st.divider()

    st.subheader("📄 Document")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**File:** {uploaded_file.name}"
        )

    with col2:

        st.write(
            f"**Size:** "
            f"{uploaded_file.size / 1024:.1f} KB"
        )


    # ========================================================
    # EXTRACT BUTTON
    # ========================================================

    if st.button(
        "🚀 Extract Data",
        type="primary",
        use_container_width=True
    ):

        temp_path = None
        excel_path = None
        gemini_file = None

        progress_bar = st.progress(0)

        status_box = st.empty()

        try:

            # =================================================
            # STEP 1 - SAVE FILE
            # =================================================

            status_box.info(
                "📥 Preparing your document..."
            )

            extension = os.path.splitext(
                uploaded_file.name
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extension
            ) as temp:

                temp.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp.name

            progress_bar.progress(10)


            # =================================================
            # STEP 2 - UPLOAD TO GEMINI
            # =================================================

            status_box.info(
                "📤 Uploading document to Gemini..."
            )

            gemini_file = client.files.upload(
                file=temp_path
            )

            progress_bar.progress(25)


            # =================================================
            # STEP 3 - WAIT UNTIL READY
            # =================================================

            gemini_file = wait_for_file_ready(
                gemini_file,
                status_box,
                progress_bar
            )


            # =================================================
            # STEP 4 - ANALYZE
            # =================================================

            status_box.info(
                "🤖 Extracting information..."
            )

            progress_bar.progress(50)


            response = None

            last_error = None


            # Retry up to 3 times
            for attempt in range(3):

                try:

                    response = client.models.generate_content(

                        model=MODEL_NAME,

                        contents=[
                            gemini_file,
                            EXTRACTION_PROMPT
                        ],

                        config={
                            "response_mime_type": "application/json"
                        }
                    )

                    break

                except Exception as e:

                    last_error = e

                    if attempt < 2:

                        status_box.warning(
                            "⚠️ Temporary Gemini issue. "
                            f"Retrying ({attempt + 2}/3)..."
                        )

                        time.sleep(3)

                    else:

                        raise last_error


            progress_bar.progress(75)

            status_box.info(
                "📊 Preparing Excel and CSV..."
            )


            # =================================================
            # STEP 5 - PARSE RESPONSE
            # =================================================

            raw_response = getattr(
                response,
                "text",
                ""
            )

            extracted_data = clean_json_response(
                raw_response
            )


            if extracted_data is None:

                raise Exception(
                    "Gemini returned an invalid JSON response."
                )


            # =================================================
            # STEP 6 - MAIN FIELDS
            # =================================================

            document_type = safe_value(
                extracted_data.get(
                    "document_type"
                )
            )

            document_number = safe_value(
                extracted_data.get(
                    "document_number"
                )
            )

            document_date = safe_value(
                extracted_data.get(
                    "date"
                )
            )

            supplier = safe_value(
                extracted_data.get(
                    "supplier"
                )
            )

            customer = safe_value(
                extracted_data.get(
                    "customer"
                )
            )

            supplier_gstin = safe_value(
                extracted_data.get(
                    "supplier_gstin"
                )
            )

            customer_gstin = safe_value(
                extracted_data.get(
                    "customer_gstin"
                )
            )

            currency = safe_value(
                extracted_data.get(
                    "currency"
                )
            )

            subtotal = safe_value(
                extracted_data.get(
                    "subtotal"
                )
            )

            cgst = safe_value(
                extracted_data.get(
                    "cgst"
                )
            )

            sgst = safe_value(
                extracted_data.get(
                    "sgst"
                )
            )

            igst = safe_value(
                extracted_data.get(
                    "igst"
                )
            )

            tax = safe_value(
                extracted_data.get(
                    "tax"
                )
            )

            total = safe_value(
                extracted_data.get(
                    "total"
                )
            )


            # =================================================
            # STEP 7 - LINE ITEMS
            # =================================================

            line_items = extracted_data.get(
                "line_items",
                []
            )

            if not isinstance(
                line_items,
                list
            ):

                line_items = []


            rows = []

            for item in line_items:

                if not isinstance(
                    item,
                    dict
                ):
                    continue

                rows.append({

                    "Description": safe_value(
                        item.get(
                            "description"
                        )
                    ),

                    "Quantity": safe_value(
                        item.get(
                            "quantity"
                        )
                    ),

                    "Unit": safe_value(
                        item.get(
                            "unit"
                        )
                    ),

                    "Unit Price": safe_value(
                        item.get(
                            "unit_price"
                        )
                    ),

                    "Tax Rate": safe_value(
                        item.get(
                            "tax_rate"
                        )
                    ),

                    "Tax Amount": safe_value(
                        item.get(
                            "tax_amount"
                        )
                    ),

                    "Line Total": safe_value(
                        item.get(
                            "line_total"
                        )
                    )

                })


            line_items_df = pd.DataFrame(
                rows,
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


            # =================================================
            # STEP 8 - SUMMARY
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


            # =================================================
            # STEP 9 - CREATE EXCEL
            # =================================================

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
            # STEP 10 - COMPLETE
            # =================================================

            progress_bar.progress(100)

            status_box.success(
                "✅ Extraction completed successfully!"
            )


            # =================================================
            # DISPLAY RESULTS
            # =================================================

            st.divider()

            st.subheader(
                "📋 Extracted Information"
            )


            c1, c2, c3 = st.columns(3)


            with c1:

                st.write("**Document Type**")
                st.write(
                    document_type or "Not found"
                )

                st.write("**Document Number**")
                st.write(
                    document_number or "Not found"
                )

                st.write("**Date**")
                st.write(
                    document_date or "Not found"
                )


            with c2:

                st.write("**Supplier / Vendor**")
                st.write(
                    supplier or "Not found"
                )

                st.write("**Supplier GSTIN**")
                st.write(
                    supplier_gstin or "Not found"
                )

                st.write("**Customer**")
                st.write(
                    customer or "Not found"
                )


            with c3:

                st.write("**Customer GSTIN**")
                st.write(
                    customer_gstin or "Not found"
                )

                st.write("**Currency**")
                st.write(
                    currency or "Not found"
                )

                st.write("**Grand Total**")
                st.write(
                    total or "Not found"
                )


            # =================================================
            # AMOUNT SUMMARY
            # =================================================

            st.subheader(
                "💰 Amount Summary"
            )

            amount_df = pd.DataFrame({

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
                amount_df,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # LINE ITEMS
            # =================================================

            st.subheader(
                f"🧾 Line Items ({len(line_items_df)})"
            )


            if not line_items_df.empty:

                edited_df = st.data_editor(

                    line_items_df,

                    use_container_width=True,

                    num_rows="dynamic",

                    key="line_items_editor"

                )

            else:

                edited_df = line_items_df

                st.info(
                    "No line items were detected."
                )


            # =================================================
            # DOWNLOAD
            # =================================================

            st.divider()

            st.subheader(
                "⬇️ Download Results"
            )


            # Create Excel again using edited data
            final_excel_path = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ).name


            with pd.ExcelWriter(
                final_excel_path,
                engine="openpyxl"
            ) as writer:

                summary_df.to_excel(
                    writer,
                    sheet_name="Summary",
                    index=False
                )

                edited_df.to_excel(
                    writer,
                    sheet_name="Line Items",
                    index=False
                )


            with open(
                final_excel_path,
                "rb"
            ) as f:

                excel_bytes = f.read()


            csv_bytes = edited_df.to_csv(
                index=False
            ).encode(
                "utf-8"
            )


            c1, c2 = st.columns(2)


            with c1:

                st.download_button(

                    "📊 Download Excel",

                    data=excel_bytes,

                    file_name="nexora_extracted_data.xlsx",

                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),

                    use_container_width=True

                )


            with c2:

                st.download_button(

                    "📄 Download CSV",

                    data=csv_bytes,

                    file_name="nexora_line_items.csv",

                    mime="text/csv",

                    use_container_width=True

                )


            st.success(
                "🎉 Your Excel and CSV files are ready."
            )


            # =================================================
            # DEBUG JSON
            # =================================================

            with st.expander(
                "🔍 View extracted JSON"
            ):

                st.json(
                    extracted_data
                )


            # =================================================
            # CLEAN EXCEL
            # =================================================

            try:

                os.remove(
                    final_excel_path
                )

            except Exception:

                pass


        except Exception as e:

            progress_bar.empty()

            status_box.empty()

            st.error(
                "❌ Document processing failed."
            )

            st.warning(
                "Please read the detailed error below. "
                "If this happens again, send me the screenshot."
            )

            with st.expander(
                "🔧 Technical error"
            ):

                st.exception(e)


        finally:

            # =================================================
            # CLEAN TEMP FILE
            # =================================================

            if temp_path:

                try:

                    os.remove(
                        temp_path
                    )

                except Exception:

                    pass
