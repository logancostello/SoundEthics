import os
from flask import Blueprint, send_from_directory, url_for
import config

download_bp = Blueprint("download", __name__)


@download_bp.get("/stems/<folder>/<filename>")
def download_stem(folder: str, filename: str):
    """Serve a single stem file from a named subfolder."""
    directory = os.path.join(config.STEM_FOLDER, folder)
    return send_from_directory(directory, filename)


@download_bp.get("/stems/<folder>")
def list_stems(folder: str):
    """Return an HTML page with download links for all stems in a folder."""
    directory = os.path.join(config.STEM_FOLDER, folder)
    filenames = os.listdir(directory)

    links = "".join(
        f'<a href="{url_for("download.download_stem", folder=folder, name=f)}">Download {f}</a><br>'
        for f in filenames
    )
    return links or "<p>No stems found.</p>"


@download_bp.get("/generated/<filename>")
def download_generated(filename: str):
    """Serve a generated audio file."""
    return send_from_directory(config.GENERATED_FOLDER, filename)