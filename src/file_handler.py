
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image, UnidentifiedImageError


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_PIXELS = 25_000_000


def process_uploaded_file(uploaded_file):

    if uploaded_file is None:
        raise ValueError("Please upload an invoice.")

    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 10 MB.")

    extension = Path(uploaded_file.name or "").suffix.lower()

    # Process image
    if extension in [".png", ".jpg", ".jpeg"]:

        try:
            image = Image.open(BytesIO(file_bytes))
            image.verify()

            # Reopen after verification
            image = Image.open(BytesIO(file_bytes))
            image.load()
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions exceed the supported limit.")
            expected_format = "PNG" if extension == ".png" else "JPEG"
            if image.format != expected_format:
                raise ValueError(
                    f"File content does not match the {extension} extension."
                )

            mime_type = (
                "image/png"
                if extension == ".png"
                else "image/jpeg"
            )

            return file_bytes, mime_type

        except (UnidentifiedImageError, OSError, ValueError) as error:
            raise ValueError(
                "Invalid or corrupted image file."
            ) from error

    # Process PDF
    elif extension == ".pdf":

        document = None
        try:
            document = fitz.open(
                stream=file_bytes,
                filetype="pdf"
            )

            if document.page_count == 0:
                raise ValueError("PDF contains no pages.")

            if document.page_count > 20:
                raise ValueError(
                    "PDF contains too many pages. Maximum is 20."
                )

            # Extract first page as an image
            page = document.load_page(0)

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            image_bytes = pixmap.tobytes("png")

            return image_bytes, "image/png"

        except Exception as error:
            raise ValueError(
                f"Unable to process PDF: {error}"
            ) from error
        finally:
            if document is not None:
                document.close()

    else:
        raise ValueError(
            "Unsupported file format. "
            "Please upload PNG, JPG, JPEG or PDF."
        )
