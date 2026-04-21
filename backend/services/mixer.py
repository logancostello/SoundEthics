import numpy as np
import librosa
import soundfile as sf
from typing import Optional


def _db_to_amp(db: float) -> float:
    return 10 ** (db / 20.0)


def _ensure_2d(y: np.ndarray) -> np.ndarray:
    """Guarantee audio array is (channels, samples)."""
    return np.expand_dims(y, axis=0) if y.ndim == 1 else y


def _pad_to_length(y: np.ndarray, target_len: int) -> np.ndarray:
    """Zero-pad the samples dimension to `target_len`."""
    if y.shape[1] < target_len:
        y = np.pad(y, ((0, 0), (0, target_len - y.shape[1])))
    return y


def _match_channels(y: np.ndarray, target_channels: int) -> np.ndarray:
    """Convert mono<->stereo as needed to match `target_channels`."""
    if y.shape[0] == target_channels:
        return y
    if y.shape[0] == 1 and target_channels == 2:
        return np.vstack([y, y])
    if y.shape[0] == 2 and target_channels == 1:
        return np.mean(y, axis=0, keepdims=True)
    raise ValueError(f"Unsupported channel conversion: {y.shape[0]} -> {target_channels}")


def _peak_normalize(y: np.ndarray, headroom_db: float = -1.0) -> np.ndarray:
    """Normalize so the peak sits at `headroom_db` below full scale."""
    peak = np.max(np.abs(y))
    if peak == 0:
        return y
    return y * (_db_to_amp(headroom_db) / peak)


def combine_wavs(
    wav_paths: list,
    output_path: str,
    gains_db: Optional[list] = None,
    master_headroom_db: float = -1.0,
) -> None:
    """
    Mix any number of .wav files together and write the result to `output_path`.

    Args:
        wav_paths:           Paths to the input .wav files.
        output_path:         Destination path for the mixed file.
        gains_db:            Per-file gain in dB (defaults to 0 dB for all).
        master_headroom_db:  Peak ceiling for the final mix (default -1.0 dB).

    Raises:
        ValueError: If `wav_paths` is empty or `gains_db` length mismatches.
    """
    if not wav_paths:
        raise ValueError("wav_paths must contain at least one file.")

    gains_db = gains_db or [0.0] * len(wav_paths)

    if len(gains_db) != len(wav_paths):
        raise ValueError("gains_db must be the same length as wav_paths.")

    # Use the first file to set the reference sample rate and channel count.
    ref, target_sr = librosa.load(wav_paths[0], sr=None, mono=False)
    ref = _ensure_2d(ref)
    target_channels = ref.shape[0]

    stems = []
    for path, gain_db in zip(wav_paths, gains_db):
        y, sr = librosa.load(path, sr=None, mono=False)
        y = _ensure_2d(y)

        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr, axis=-1)

        y = _match_channels(y, target_channels)
        y = y * _db_to_amp(gain_db)
        stems.append(y)

    max_len = max(s.shape[1] for s in stems)
    stems = [_pad_to_length(s, max_len) for s in stems]

    mix = _peak_normalize(np.sum(stems, axis=0), headroom_db=master_headroom_db)

    # soundfile expects (samples, channels)
    sf.write(output_path, mix.T, target_sr)
    print(f"✅ Mixed {len(wav_paths)} stems → {output_path}")