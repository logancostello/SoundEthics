from typing import Optional
from config import ALLOWED_EXTENSIONS, ALLOWED_STEMS


def allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed audio extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_stem(stem: str) -> bool:
    """Return True if the stem type is supported."""
    return stem in ALLOWED_STEMS


def validate_file_and_stem(file, stem: str) -> Optional[str]:
    """
    Validate a (file, stem) pair.
    Returns an error message string if invalid, or None if valid.
    """
    if not file or not file.filename:
        return "No file provided."
    if not allowed_file(file.filename):
        return f"File type not allowed for '{file.filename}'."
    if not allowed_stem(stem):
        return f"Stem type '{stem}' is not allowed. Choose from: {ALLOWED_STEMS}."
    return None