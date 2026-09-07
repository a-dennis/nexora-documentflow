import streamlit as st
import pandas as pd
import json
import re
import time

from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Nexora DocumentFlow",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# SIMPLE UI
# ============================================================

st.markdown("""
<style>

.title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 4px;
}

.subtitle {
    color: #666;
    font-size: 16px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


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
# GEMINI
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
        f"❌ Gemini initialization failed: {e}"
    )

    st.stop()


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.1-flash-lite"


# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
You are a fast and highly accurate invoice/document extraction engine.

Analyze the uploaded document and return structured information.

IMPORTANT:

- Extract only information actually visible.
- Never invent values.
- If a value is missing, return "".
- Extract every line item.
- Do not merge line items.
- Preserve numbers accurately.
- Preserve invoice numbers and dates exactly.
- For Indian GST invoices identify CGST, SGST and IGST separately when visible.
- Do not explain your answer.
- Return ONLY valid JSON.

Use exactly this JSON structure:

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

def clean_json(text):

    if not text:
        return None

    text = text.strip()

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
    help="Upload an invoice, receipt, purchase order or business document."
)


# ============================================================
# MAIN PROCESS
# ============================================================

if uploaded_file is not None:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**File:** {uploaded_file.name}"
        )

    with col2:

        st.write(
            f"**Size:** {uploaded_file.size / 1024:.1f} KB"
        )


    # ========================================================
    # EXTRACT
    # ========================================================

    if st.button(
        "⚡ Extract",
        type="primary",
        use_container_width=True
    ):

        start_time = time.time()

        progress = st.progress(0)

        status = st.empty()

        try:

            # ------------------------------------------------
            # READ FILE DIRECTLY
            # ------------------------------------------------

            status.info(
                "📖 Reading document..."
            )

            file_bytes = uploaded_file.getvalue()

            progress.progress(15)


            # ------------------------------------------------
            # MIME TYPE
            # ------------------------------------------------

            file_name = uploaded_file.name.lower()

            if file_name.endswith(".pdf"):

                mime_type = "application/pdf"

            elif file_name.endswith(".png"):

                mime_type = "image/png"

            elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):

                mime_type = "image/jpeg"

            else:

                st.error(
                    "Unsupported file type."
                )

                st.stop()


            # ------------------------------------------------
            # DIRECT INLINE FILE
            # ------------------------------------------------

            document_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=mime_type
            )


            progress.progress(30)

            status.info(
                "🤖 Extracting document data..."
            )


            # ------------------------------------------------
            # GEMINI REQUEST
            # ------------------------------------------------

            response = None

            last_error = None


            # Only ONE retry for temporary 500 errors.
            # This prevents long waiting.

            for attempt in range(2):

                try:

                    response = client.models.generate_content(

                        model=MODEL_NAME,

                        contents=[
                            document_part,
                            EXTRACTION_PROMPT
                        ],

                        config=types.GenerateContentConfig(

                            response_mime_type="application/json",

                            thinking_config=types.ThinkingConfig(
                                thinking_level="minimal"
                            )

                        )
                    )

                    break


                except Exception as e:

                    last_error = e

                    error_text = str(e)

                    if (
                        "500" in error_text
                        or "INTERNAL" in error_text.upper()
                        or "503" in error_text
                        or "UNAVAILABLE" in error_text.upper()
                    ):

                        if attempt == 0:

                            status.warning(
                                "⚠️ Gemini had a temporary server issue. "
                                "Retrying once..."
                            )

                            time.sleep(1.5)

                        else:

                            raise last_error

                    else:

                        raise


            progress.progress(75)


            # ------------------------------------------------
            # GET RESPONSE
            # ------------------------------------------------

            raw_text = getattr(
                response,
                "text",
                ""
            )


            extracted = clean_json(
                raw_text
            )


            if extracted is None:

                raise Exception(
                    "Gemini returned invalid JSON."
                )


            # =================================================
            # EXTRACT MAIN FIELDS
            # =================================================

            document_type = safe_value(
                extracted.get("document_type")
            )

            document_number = safe_value(
                extracted.get("document_number")
            )

            document_date = safe_value(
                extracted.get("date")
            )

            supplier = safe_value(
                extracted.get("supplier")
            )

            customer = safe_value(
                extracted.get("customer")
            )

            supplier_gstin = safe_value(
                extracted.get("supplier_gstin")
            )

            customer_gstin = safe_value(
                extracted.get("customer_gstin")
            )

            currency = safe_value(
                extracted.get("currency")
            )

            subtotal = safe_value(
                extracted.get("subtotal")
            )

            cgst = safe_value(
                extracted.get("cgst")
            )

            sgst = safe_value(
                extracted.get("sgst")
            )

            igst = safe_value(
                extracted.get("igst")
            )

            tax = safe_value(
                extracted.get("tax")
            )

            total = safe_value(
                extracted.get("total")
            )


            # =================================================
            # LINE ITEMS
            # =================================================

            line_items = extracted.get(
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
                        item.get("description")
                    ),

                    "Quantity": safe_value(
                        item.get("quantity")
                    ),

                    "Unit": safe_value(
                        item.get("unit")
                    ),

                    "Unit Price": safe_value(
                        item.get("unit_price")
                    ),

                    "Tax Rate": safe_value(
                        item.get("tax_rate")
                    ),

                    "Tax Amount": safe_value(
                        item.get("tax_amount")
                    ),

                    "Line Total": safe_value(
                        item.get("line_total")
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
            # SUMMARY
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
            # CREATE EXCEL IN MEMORY
            # =================================================

            import io

            excel_buffer = io.BytesIO()


            with pd.ExcelWriter(
                excel_buffer,
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


            excel_bytes = excel_buffer.getvalue()


            # =================================================
            # CSV
            # =================================================

            csv_bytes = line_items_df.to_csv(
                index=False
            ).encode("utf-8")


            # =================================================
            # FINISHED
            # =================================================

            elapsed = time.time() - start_time

            progress.progress(100)

            status.success(
                f"✅ Extraction completed in {elapsed:.1f} seconds"
            )


            # =================================================
            # RESULTS
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
            # AMOUNTS
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
                    "No line items detected."
                )


            # =================================================
            # DOWNLOAD
            # =================================================

            st.divider()

            st.subheader(
                "⬇️ Download Results"
            )


            # Rebuild Excel using edited data

            final_excel = io.BytesIO()


            with pd.ExcelWriter(
                final_excel,
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


            final_excel_bytes = (
                final_excel.getvalue()
            )


            final_csv_bytes = (
                edited_df
                .to_csv(index=False)
                .encode("utf-8")
            )


            c1, c2 = st.columns(2)


            with c1:

                st.download_button(

                    label="📊 Download Excel",

                    data=final_excel_bytes,

                    file_name=(
                        "nexora_extracted_data.xlsx"
                    ),

                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),

                    use_container_width=True

                )


            with c2:

                st.download_button(

                    label="📄 Download CSV",

                    data=final_csv_bytes,

                    file_name=(
                        "nexora_line_items.csv"
                    ),

                    mime="text/csv",

                    use_container_width=True

                )


            st.success(
                "🎉 Excel and CSV are ready."
            )


            # =================================================
            # DEBUG
            # =================================================

            with st.expander(
                "🔍 View extracted JSON"
            ):

                st.json(
                    extracted
                )


        except Exception as e:

            progress.empty()

            status.empty()

            st.error(
                "❌ Extraction failed."
            )

            error_string = str(e)


            if (
                "500" in error_string
                or "INTERNAL" in error_string.upper()
            ):

                st.warning(
                    "Gemini returned a temporary internal server "
                    "error. This is not an Excel or Streamlit "
                    "processing error."
                )

                st.info(
                    "Please click Extract again. "
                    "The optimized version retries only once "
                    "to avoid unnecessary waiting."
                )


            with st.expander(
                "🔧 Technical details"
            ):

                st.exception(e)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Nexora DocumentFlow • AI-powered document extraction"
)

st.caption(
    "Use sample/non-confidential documents while testing."
)
