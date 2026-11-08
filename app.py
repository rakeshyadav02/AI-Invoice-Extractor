
import json
import streamlit as st
import pandas as pd

from src.file_handler import process_uploaded_file
from src.extractor import extract_invoice
from src.validator import validate_invoice


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Invoice Extractor",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# 2. APPLICATION HEADER
# --------------------------------------------------

st.title("📄 AI-Powered Invoice Data Extractor")

st.markdown(
    """
    Upload an invoice image or PDF. Our AI system will
    automatically extract invoice details, identify items,
    and validate financial calculations.
    """
)

st.divider()


# --------------------------------------------------
# 3. FILE UPLOAD SECTION
# --------------------------------------------------

st.subheader("📤 Upload Your Invoice")

uploaded_file = st.file_uploader(
    "Choose an invoice file",
    type=["png", "jpg", "jpeg", "pdf"],
    help="Supported formats: PNG, JPG, JPEG and PDF. Maximum size: 10 MB."
)


# --------------------------------------------------
# 4. DISPLAY UPLOADED FILE
# --------------------------------------------------

if uploaded_file is not None:

    st.success(
        f"File uploaded successfully: {uploaded_file.name}"
    )

    if uploaded_file.type.startswith("image/"):

        st.image(
            uploaded_file,
            caption="Uploaded Invoice",
            width=500
        )

    else:
        st.info(
            "PDF uploaded. The first page will be processed."
        )


# --------------------------------------------------
# 5. EXTRACT INVOICE BUTTON
# --------------------------------------------------

if st.button(
    "🚀 Extract Invoice Information",
    type="primary",
    disabled=uploaded_file is None
):

    try:

        with st.spinner(
            "Processing invoice with Gemini AI..."
        ):

            # Process uploaded file
            image_bytes, mime_type = process_uploaded_file(
                uploaded_file
            )

            # Extract invoice information
            invoice = extract_invoice(
                image_bytes,
                mime_type
            )

            # Validate invoice calculations
            validation = validate_invoice(invoice)

            # Save results in session state
            st.session_state["invoice"] = invoice
            st.session_state["validation"] = validation
            st.session_state["filename"] = uploaded_file.name

        st.success(
            "Invoice extraction completed successfully!"
        )

    except Exception as error:

        st.error(
            f"Invoice processing failed: {error}"
        )


# --------------------------------------------------
# 6. DISPLAY EXTRACTION RESULTS
# --------------------------------------------------

if "invoice" in st.session_state:

    invoice = st.session_state["invoice"]

    validation = st.session_state["validation"]

    st.divider()

    st.header("📋 Extracted Invoice Information")


    # Invoice basic details
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Invoice Number",
            invoice.invoice_number or "Not available"
        )

    with col2:
        st.metric(
            "Invoice Date",
            invoice.invoice_date or "Not available"
        )

    with col3:
        st.metric(
            "Currency",
            invoice.currency or "Not available"
        )


    st.subheader("Supplier Information")

    st.write(
        invoice.supplier_name or "Supplier name not available"
    )


    # --------------------------------------------------
    # 7. DISPLAY ITEM DETAILS
    # --------------------------------------------------

    st.subheader("📦 Invoice Items")

    if invoice.items:

        items_data = []

        for item in invoice.items:

            items_data.append({
                "Description": item.description,
                "Quantity": (
                    float(item.quantity)
                    if item.quantity is not None else None
                ),
                "Unit Price": (
                    float(item.unit_price)
                    if item.unit_price is not None else None
                ),
                "Total Amount": (
                    float(item.total_amount)
                    if item.total_amount is not None else None
                )
            })

        items_df = pd.DataFrame(items_data)

        st.dataframe(
            items_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning("No invoice items were extracted.")


    # --------------------------------------------------
    # 8. DISPLAY FINANCIAL SUMMARY
    # --------------------------------------------------

    st.subheader("💰 Financial Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Subtotal",
            (
                f"{invoice.currency or ''} {invoice.subtotal:,.2f}"
                if invoice.subtotal is not None else "N/A"
            )
        )

    with col2:
        st.metric(
            "VAT Amount",
            (
                f"{invoice.currency or ''} {invoice.vat_amount:,.2f}"
                if invoice.vat_amount is not None else "N/A"
            )
        )

    with col3:
        st.metric(
            "Grand Total",
            (
                f"{invoice.currency or ''} {invoice.total_amount:,.2f}"
                if invoice.total_amount is not None else "N/A"
            )
        )


    # --------------------------------------------------
    # 9. VALIDATION RESULTS
    # --------------------------------------------------

    st.divider()

    st.header("🔍 Invoice Validation")

    if validation["is_valid"]:

        st.success(
            "Financial validation passed: "
            "No calculation errors were detected."
        )

    else:

        st.error(
            "Financial validation failed. "
            "Please review the following errors."
        )

    if validation["errors"]:

        st.subheader("Errors")

        for error in validation["errors"]:
            st.error(error)

    if validation["warnings"]:

        st.subheader("Warnings")

        for warning in validation["warnings"]:
            st.warning(warning)


    # --------------------------------------------------
    # 10. JSON OUTPUT
    # --------------------------------------------------

    st.divider()

    st.header("📄 Structured JSON Output")

    json_output = invoice.model_dump_json(indent=2)

    st.json(json.loads(json_output))

    st.download_button(
        label="⬇️ Download Invoice JSON",
        data=json_output,
        file_name="extracted_invoice.json",
        mime="application/json"
    )


    # --------------------------------------------------
    # 11. PROCESSING SUMMARY
    # --------------------------------------------------

    st.divider()

    st.caption(
        f"Processed file: {st.session_state['filename']}"
    )

    st.caption(
        "Powered by Python, Streamlit and Google Gemini AI."
    )


# --------------------------------------------------
# 12. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Invoice Extractor | Invoice information should "
    "be reviewed before financial or accounting use."
)
