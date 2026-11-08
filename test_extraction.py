import json

import pytest

from src.extractor import clean_json_response, extract_invoice


def test_clean_json_response_removes_json_code_fences():
    assert clean_json_response('```json\n{"total_amount": 10}\n```') == (
        '{"total_amount": 10}'
    )


def test_clean_json_response_rejects_empty_response():
    with pytest.raises(ValueError, match="empty response"):
        clean_json_response("")


def test_extract_invoice_rejects_invalid_input_before_api_call():
    with pytest.raises(ValueError, match="image is empty"):
        extract_invoice(b"", "image/png")

    with pytest.raises(ValueError, match="Unsupported image format"):
        extract_invoice(b"invoice", "application/pdf")


def test_cleaned_response_is_valid_json():
    response = clean_json_response("```json\n{\"total_amount\": 113565}\n```")
    assert json.loads(response)["total_amount"] == 113565
