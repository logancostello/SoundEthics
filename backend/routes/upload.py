import os
from flask import Blueprint, request, jsonify
from utils import validate_file_and_stem
from services.audio import process_upload
from services.mixer import combine_wavs
import config

upload_bp = Blueprint("upload", __name__)

# Each slot maps a request field name to its stem-type field name.
FILE_SLOTS = [
    ("file1", "stem1"),
    ("file2", "stem2"),
]


@upload_bp.post("/upload_file")
def upload_file():
    """
    Accept up to two audio files with associated stem types, stem-split each,
    mix the results, and return a URL to the generated file.

    Form fields:
        file1 / stem1  — first audio file and its stem type
        file2 / stem2  — (optional) second audio file and its stem type

    Stem types: "drums" | "melody"
    """
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.STEM_FOLDER, exist_ok=True)
    os.makedirs(config.GENERATED_FOLDER, exist_ok=True)

    stem_paths: dict[str, str] = {}

    for file_field, stem_field in FILE_SLOTS:
        file = request.files.get(file_field)
        stem = request.form.get(stem_field, "")

        # Skip empty slots silently — only one file is required.
        if not file or not file.filename:
            continue

        error = validate_file_and_stem(file, stem)
        if error:
            return jsonify({"error": error}), 400

        # Last write wins if the same stem type is submitted twice.
        stem_paths[stem] = process_upload(
            file, stem,
            upload_folder=config.UPLOAD_FOLDER,
            stem_folder=config.STEM_FOLDER,
        )

    if not stem_paths:
        return jsonify({"error": "At least one valid audio file is required."}), 400

    output_path = os.path.join(config.GENERATED_FOLDER, config.GENERATED_FILENAME)
    combine_wavs(list(stem_paths.values()), output_path)

    return jsonify({"url": f"/generated/{config.GENERATED_FILENAME}"})