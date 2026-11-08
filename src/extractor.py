
import json
import re

from google.genai import types
from pydantic import ValidationError

from src.gemini_client import get_gemini_client, get_model_name
from src.schemas import InvoiceData


# --------------------------------------------------
# 1. INVOICE EXTRACTION PROMPT
# --------------------------------------------------

INVOICE_EXTRACTION_PROMPT = """
You are an expert invoice data extraction assistant.

Your task is to carefully analyze the COMPLETE invoice image
and extract all available information accurately.

Extract the following fields:

1. invoice_number
2. invoice_date
3. supplier_name
4. currency
5. items:
   - description
   - quantity
   - unit_price
   - total_amount
6. subtotal
7. vat_amount
8. vat_percentage
9. total_amount (GRAND TOTAL)

IMPORTANT GRAND TOTAL INSTRUCTIONS:

- Carefully inspect the bottom section of the invoice.
- Identify the final payable amount.
- Look for labels such as:
  "Grand Total"
  "Total Amount"
  "Net Payable"
  "Amount Due"
  "Total Payable"
  "Invoice Total"

- Extract the amount associated with the FINAL TOTAL label.
- Do NOT confuse subtotal with grand total.
- Do NOT return the subtotal as the grand total.
- VAT must be extracted separately.
- If both subtotal and VAT are visible, extract them separately.
- If a grand total is explicitly printed, use that printed amount.
- Do not calculate a replacement when a printed grand total exists.
- If the grand total is genuinely not visible, return null.
- Never invent invoice information.

GENERAL INSTRUCTIONS:

- Read the entire invoice, including its bottom section.
- Preserve original product descriptions.
- Extract every visible invoice item.
- Do not skip invoice items.
- Use null for missing individual values.
- Monetary values must be numeric.
- Do not include currency symbols inside numeric values.
- Preserve the original currency code where identifiable.
- Return only valid JSON.
- Do not include Markdown formatting or explanations.

EXPECTED JSON STRUCTURE:

{
    "invoice_number": null,
    "invoice_date": null,
    "supplier_name": null,
    "currency": "NPR",
    "items": [
        {
            "description": null,
            "quantity": null,
            "unit_price": null,
            "total_amount": null
        }
    ],
    "subtotal": null,
    "vat_amount": null,
    "vat_percentage": null,
    "total_amount": null
}
"""


# --------------------------------------------------
# 2. CLEAN GEMINI JSON RESPONSE
# --------------------------------------------------

def clean_json_response(response_text):

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    response_text = response_text.strip()

    # Remove Markdown code fences if present
    response_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )

    return response_text.strip()


# --------------------------------------------------
# 3. EXTRACT INVOICE INFORMATION
# --------------------------------------------------

def extract_invoice(image_bytes, mime_type):

    if not image_bytes:
        raise ValueError("Invoice image is empty.")

    if mime_type not in ["image/png", "image/jpeg"]:
        raise ValueError(
            "Unsupported image format. "
            "Please provide PNG or JPEG."
        )

    model_name = "<unknown>"

    try:

        # Create Gemini API client
        client = get_gemini_client()
        model_name = get_model_name()

        # Prepare invoice image for Gemini
        invoice_image = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        # Send image and extraction instructions
        response = client.models.generate_content(

            model=model_name,

            contents=[
                INVOICE_EXTRACTION_PROMPT,
                invoice_image
            ],

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                temperature=0
            )
        )

        # Check Gemini response
        if not response.text:
            raise ValueError(
                "Gemini did not return any invoice information."
            )

        # Clean JSON response
        cleaned_response = clean_json_response(
            response.text
        )

        # Convert JSON into Python dictionary
        extracted_json = json.loads(
            cleaned_response
        )

        if not isinstance(extracted_json, dict):
            raise ValueError(
                "Gemini response must be a JSON object."
            )

        # Normalize possible alternative grand total keys
        if extracted_json.get("total_amount") is None:

            alternative_keys = [
                "grand_total",
                "total_payable",
                "amount_due",
                "net_payable",
                "invoice_total"
            ]

            for key in alternative_keys:

                if extracted_json.get(key) is not None:

                    extracted_json["total_amount"] = (
                        extracted_json[key]
                    )

                    break

        # Validate extracted data using Pydantic
        invoice_data = InvoiceData.model_validate(
            extracted_json
        )

        return invoice_data

    except json.JSONDecodeError as error:

        raise ValueError(
            "Gemini returned invalid JSON. "
            "Please try another invoice image."
        ) from error

    except ValidationError as error:

        raise ValueError(
            f"Invoice data validation failed: {error}"
        ) from error

    except ValueError:
        raise

    except Exception as error:

        raise RuntimeError(
            f"Invoice extraction failed using model '{model_name}': {error}"
        ) from error
