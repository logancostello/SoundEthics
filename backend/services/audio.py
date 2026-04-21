import os
from typing import Optional
import demucs.api
from werkzeug.utils import secure_filename

# Demucs maps "melody" to its internal "other" stem.
STEM_ALIASES = {"melody": "other"}

# Initialized once at import time so the model isn't reloaded per request.
_separator = demucs.api.Separator()


def split_stem(audio_path: str, desired_stem: str):
    """
    Run Demucs on `audio_path` and return the tensor for `desired_stem`.

    Args:
        audio_path:    Path to the source audio file.
        desired_stem:  One of the app's supported stem names ("drums", "melody").

    Returns:
        torch.Tensor of the isolated stem.

    Raises:
        ValueError: If the stem is not found in Demucs output.
    """
    demucs_stem = STEM_ALIASES.get(desired_stem, desired_stem)
    _, separated = _separator.separate_audio_file(audio_path)

    if demucs_stem not in separated:
        raise ValueError(
            f"Stem '{desired_stem}' (mapped to '{demucs_stem}') not found in Demucs output. "
            f"Available: {list(separated.keys())}"
        )

    return separated[demucs_stem]


def save_stem(stem_tensor, stem_name: str, stem_folder: str, base_name: str) -> str:
    """
    Write a stem tensor to disk as a .wav file.

    Returns:
        The full path to the saved stem file.
    """
    os.makedirs(stem_folder, exist_ok=True)
    filename = f"{base_name}_{stem_name}.wav"
    filepath = os.path.join(stem_folder, filename)
    demucs.api.save_audio(stem_tensor, filepath, samplerate=_separator.samplerate)
    return filepath


def process_upload(file, stem_type: str, upload_folder: str, stem_folder: str) -> str:
    """
    Save an uploaded file, run stem splitting, and persist the result.

    Args:
        file:          Werkzeug FileStorage object from the request.
        stem_type:     Desired stem ("drums" or "melody").
        upload_folder: Where to save the raw upload.
        stem_folder:   Where to save the extracted stem.

    Returns:
        Path to the saved stem file.
    """
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    upload_path = os.path.join(upload_folder, filename)
    file.save(upload_path)

    stem_tensor = split_stem(upload_path, stem_type)
    base_name = os.path.splitext(filename)[0]
    return save_stem(stem_tensor, stem_type, stem_folder, base_name)