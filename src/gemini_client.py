
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_MODEL_NAME = "gemini-2.5-flash"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_model_name() -> str:
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL_NAME).strip()
    if not model_name:
        raise ValueError(
            "GEMINI_MODEL is empty. Set it to a supported Gemini model."
        )
    return model_name


def get_gemini_client() -> genai.Client:

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "GEMINI_API_KEY is missing or empty. "
            "Add a valid Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=api_key.strip(),
        http_options=types.HttpOptions(api_version="v1beta"),
    )


def test_gemini_connection() -> str:

    client = get_gemini_client()
    model_name = get_model_name()

    response = client.models.generate_content(
        model=model_name,
        contents="Reply with exactly: Gemini connection successful."
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty connection-test response.")

    return response.text
