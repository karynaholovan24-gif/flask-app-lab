from pathlib import Path
from uuid import uuid4
from io import BytesIO

from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def save_product_image(image_file):
    if image_file is None or not image_file.filename:
        return ""

    original_name = secure_filename(image_file.filename)

    if "." not in original_name:
        raise ValueError("Файл повинен мати розширення.")

    extension = original_name.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Дозволені лише зображення JPG, JPEG та PNG."
        )

    file_bytes = image_file.read()

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            image.verify()

        with Image.open(BytesIO(file_bytes)) as image:
            actual_format = image.format

    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError(
            "Вибраний файл не є коректним зображенням."
        )

    if actual_format not in {"JPEG", "PNG"}:
        raise ValueError(
            "Дозволені лише зображення JPG, JPEG та PNG."
        )

    if extension in {"jpg", "jpeg"} and actual_format != "JPEG":
        raise ValueError(
            "Розширення файлу не відповідає формату зображення."
        )

    if extension == "png" and actual_format != "PNG":
        raise ValueError(
            "Розширення файлу не відповідає формату зображення."
        )

    upload_folder = Path(current_app.static_folder) / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid4().hex}.{extension}"
    file_path = upload_folder / unique_filename

    file_path.write_bytes(file_bytes)

    return f"uploads/{unique_filename}"