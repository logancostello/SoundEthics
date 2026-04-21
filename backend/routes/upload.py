import os
from flask import Blueprint, request, jsonify
from utils import validate_file_and_stem
from services.audio import process_upload
from services.mixer import combine_wavs
import config

upload_bp = Blueprint("upload", __name__)


@upload_bp.post("/upload_file")
def upload_file():
    """
    Accept any number of audio files with associated stem types, stem-split
    each, mix all results together, and return a URL to the generated file.

    Form fields (repeat as many times as needed):
        files  — audio file(s)
        stems  — stem type for each corresponding file ("drums" | "melody")

    The nth file is paired with the nth stem. Duplicates of the same stem
    type are allowed and will all be mixed together.
    """
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.STEM_FOLDER, exist_ok=True)
    os.makedirs(config.GENERATED_FOLDER, exist_ok=True)

    files = request.files.getlist("files")
    stems = request.form.getlist("stems")

    if not files or not any(f.filename for f in files):
        return jsonify({"error": "At least one audio file is required."}), 400

    if len(files) != len(stems):
        return jsonify({"error": f"Got {len(files)} file(s) but {len(stems)} stem type(s). They must match."}), 400

    stem_paths = []

    for file, stem in zip(files, stems):
        error = validate_file_and_stem(file, stem)
        if error:
            return jsonify({"error": error}), 400

        stem_path = process_upload(
            file, stem,
            upload_folder=config.UPLOAD_FOLDER,
            stem_folder=config.STEM_FOLDER,
        )
        stem_paths.append(stem_path)

    output_path = os.path.join(config.GENERATED_FOLDER, config.GENERATED_FILENAME)
    combine_wavs(stem_paths, output_path)

    return jsonify({"url": f"/generated/{config.GENERATED_FILENAME}"})