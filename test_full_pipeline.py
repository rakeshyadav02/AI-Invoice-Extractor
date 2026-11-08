from io import BytesIO

from PIL import Image

from src.file_handler import process_uploaded_file


class UploadedFile:
    def __init__(self, name, content):
        self.name = name
        self._content = content

    def getvalue(self):
        return self._content


def test_uploaded_png_is_normalized_for_extraction():
    image = Image.new("RGB", (20, 20), "white")
    content = BytesIO()
    image.save(content, format="PNG")

    result, mime_type = process_uploaded_file(
        UploadedFile("invoice.png", content.getvalue())
    )

    assert result == content.getvalue()
    assert mime_type == "image/png"


def test_invalid_file_type_is_rejected():
    try:
        process_uploaded_file(UploadedFile("invoice.txt", b"not an invoice"))
    except ValueError as error:
        assert "Unsupported file format" in str(error)
    else:
        raise AssertionError("Expected unsupported file format error")
