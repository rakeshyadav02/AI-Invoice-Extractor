import pytest

from src.gemini_client import get_gemini_client, get_model_name


def test_model_name_has_a_default(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert get_model_name() == "gemini-2.5-flash"


def test_missing_api_key_fails_with_actionable_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
        get_gemini_client()
