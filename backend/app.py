from flask import Flask, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import numpy as np
import demucs.api
import os
import librosa
import soundfile as sf
import pyloudnorm as pyln
from pedalboard import Pedalboard, Compressor, HighpassFilter, Limiter
import requests
import time
import urllib.parse
import json
from dotenv import load_dotenv

load_dotenv()
ACESTEP_URL = os.environ.get("ACESTEP_URL")

def generate_with_ace(audio_path, prompt, bpm, duration, inference_steps, seed, is_thinking, cover_strength, guidance_scale, key):
    payload = {
        "task_type": "text2music", # cover or text2music, unsure which is best
        "lyrics": "[Instrumental]",
        "timesignature": "4",
        "audio_format": "wav",
        "thinking" : is_thinking
    }

    # add optional parameters, if they exist
    if prompt != "null":
        payload["caption"] = prompt
    if bpm != "null": 
        payload["bpm"] = bpm
    if seed != "null":
        payload["seed"] = seed
    # TODO: make sure this is fine .. it was hard-coded before ... 
    if key != "null":
        payload["keyscale"] = key

    # set default duration to 30 seconds, since API default is 120 (faster generation)
    if duration != "null":
        payload["duration"] = duration
    else: 
        payload["duration"] = 30

    # set default inference_steps to 20 for quality output
    if inference_steps != "null":
        payload["inference_steps"] = inference_steps
    else: 
        payload["inference_steps"] = 20

    # add audio and prompt adherence if they exist
    # if not, set to default values based on our own testing with james ob
    if cover_strength != "null":
        payload["audio_cover_strength"] = cover_strength
    else: 
        payload["audio_cover_strength"] = 0.7

    if guidance_scale != "null":
        payload["guidance_scale"] = guidance_scale
    else: 
        payload["guidance_sclae"] = 0.3

    # logging
    print("AUDIO: " + str(payload["audio_cover_strength"]))
    print("PROMPT: " + str(payload["guidance_sclae"]))

    with open(audio_path, "rb") as f:
        files = {"src_audio": (os.path.basename(audio_path), f, "audio/wav")}
        resp = requests.post(f"{ACESTEP_URL}/release_task", data=payload, files=files)

    resp.raise_for_status()
    task_id = resp.json()["data"]["task_id"]

    for i in range(240):
        time.sleep(2)
        poll = requests.post(f"{ACESTEP_URL}/query_result", json={"task_id_list": [task_id]})
        results = poll.json()["data"]
        if not results:
            continue
        result = results[0]

        if result["status"] == 1:
            print("=== Generation succeeded ===")
            result_data = json.loads(result["result"])[0]

            audio_url = f"{ACESTEP_URL}{result_data['file']}"
            audio = requests.get(audio_url)

            out_path = "generated/ace_output.wav"
            os.makedirs("generated", exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(audio.content)

            return out_path

        elif result["status"] == -1:
            print("=== Generation FAILED ===")
            print("failure result:", result)
            raise RuntimeError(f"ACE-Step failed: {result.get('result')}")

    raise TimeoutError("ACE-Step timed out after 8 minutes")


'''
-----
SETUP
-----
'''

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploaded_content/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

STEM_FOLDER = "stem_content/"
app.config['STEM_FOLDER'] = STEM_FOLDER

GENERATED_FOLDER = "generated/"
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

ALLOWED_EXTENSIONS = {'wav', 'mp3'}
ALLOWED_STEMS = {"drums", "bass", "guitar", "piano", "other"}

separator = demucs.api.Separator(model="htdemucs_6s")

'''
----------------
HELPER FUNCTIONS
----------------
'''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_audio(audio_path, desired_stem):
    if desired_stem not in ALLOWED_STEMS:
        raise ValueError(f"Desired stem must be one of: {ALLOWED_STEMS}")

    origin, separated = separator.separate_audio_file(audio_path)

    for stem, source in separated.items():
        if stem == desired_stem:
            return source

    raise ValueError(f"Stem '{desired_stem}' not found in separation output")

def split_and_save(file, stem_type):
    upload_filename = secure_filename(file.filename)
    upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
    file.save(upload_filepath)

    stem_tensor = split_audio(upload_filepath, stem_type)

    base_name = os.path.splitext(upload_filename)[0]
    stem_filename = f"{base_name}_{stem_type}_split.wav"
    stem_filepath = os.path.join(app.config["STEM_FOLDER"], stem_filename)
    demucs.api.save_audio(stem_tensor, stem_filepath, samplerate=separator.samplerate)

    return stem_filepath


'''
---------
ENDPOINTS
---------
'''

@app.route("/")
def hello_world():
    return f"""<p>Hello, World!</p>
    <br>
    <a href={url_for("upload_file", _external=True)}>Upload File</a>
    """

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(STEM_FOLDER, exist_ok=True)
        os.makedirs(GENERATED_FOLDER, exist_ok=True)

        split_filepaths = {}

        prompt = request.form.get("prompt")
        bpm = request.form.get("bpm")
        duration = request.form.get("duration")
        inference_steps = request.form.get("inferenceSteps")
        seed = request.form.get("seed") or -1
        key = request.form.get("key") or ""
        is_thinking = request.form.get("isThinking") or True
        cover_strength = request.form.get("coverStrength")
        guidance_scale = request.form.get("guidanceScale")

        # read file1, file2, file3, ... until none found
        i = 1
        while True:
            file = request.files.get(f"file{i}")
            stem = request.form.get(f"stem{i}")
            if not file or not file.filename:
                break
            if not allowed_file(file.filename):
                raise ValueError(f"File {i}: file type not allowed.")
            if stem not in ALLOWED_STEMS:
                raise ValueError(f"File {i}: stem type not allowed.")
            stem_filepath = split_and_save(file, stem)
            split_filepaths[f"{stem}_{i}"] = stem_filepath 
            i += 1

        if not split_filepaths:
            raise ValueError("No conditioning files provided")

        # step 1: combine all stems
        combined_filepath = os.path.join(app.config['GENERATED_FOLDER'], "combined.wav")
        combine_wavs(list(split_filepaths.values()), combined_filepath)
        
        # step 2: generate output
        ace_output = generate_with_ace(combined_filepath, prompt, bpm, duration, inference_steps, seed, is_thinking, cover_strength, guidance_scale, key)
        generated_song_path = os.path.join(app.config['GENERATED_FOLDER'], "generated.wav")
        os.replace(ace_output, generated_song_path)

        return jsonify({"url": "/generated/generated.wav"})

    return """
        <h1>Upload & Split Audio</h1>
        <form method="post" enctype="multipart/form-data">
        <input type="file" name="file1" accept="audio/*">
        <select name="stem1" required>
            <option value="drums">drums</option>
            <option value="melody">melody</option>
        </select>
        <br>
        <input type="file" name="file2" accept="audio/*">
        <select name="stem2" required>
            <option value="drums">drums</option>
            <option value="melody">melody</option>
        </select>
        <br>
        <button type="submit">Upload</button>
        </form>
        """

@app.route('/stems/<folder>/<name>')
def download_stem(folder, name):
    dir = os.path.join(app.config["STEM_FOLDER"], folder)
    return send_from_directory(dir, name)

@app.route('/stems/<folder>')
def download_stems(folder):
    dir = os.path.join(app.config["STEM_FOLDER"], folder)
    filenames = os.listdir(dir)
    ret = ""
    for file in filenames:
        ret += f"""
        <a href={url_for('download_stem', folder=folder, name=file, _external=True)}>Download {file}</a><br>
        """
    return ret

@app.route("/generated/<name>")
def download_generated(name):
    return send_from_directory(app.config["GENERATED_FOLDER"], name)


'''
-----------
AUDIO UTILS
-----------
'''

def db_to_amp(db):
    return 10 ** (db / 20.0)

def ensure_2d(y):
    if y.ndim == 1:
        y = np.expand_dims(y, axis=0)
    return y

def pad_to_length(y, target_len):
    if y.shape[1] < target_len:
        pad_width = target_len - y.shape[1]
        y = np.pad(y, ((0, 0), (0, pad_width)))
    return y

def match_channels(y, target_channels):
    if y.shape[0] == target_channels:
        return y
    if y.shape[0] == 1 and target_channels == 2:
        return np.vstack([y, y])
    elif y.shape[0] == 2 and target_channels == 1:
        return np.mean(y, axis=0, keepdims=True)
    else:
        raise ValueError(f"Unsupported channel conversion: {y.shape[0]} -> {target_channels}")

def peak_normalize_with_headroom(y, headroom_db=-1.0):
    peak = np.max(np.abs(y))
    if peak == 0:
        return y
    target_peak = db_to_amp(headroom_db)
    return y * (target_peak / peak)

def lufs_normalize(y, sr, target_lufs=-23.0):
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y.T)
    if np.isinf(loudness) or np.isnan(loudness):
        return y
    return pyln.normalize.loudness(y.T, loudness, target_lufs).T

def master_mix(y, sr):
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=40),
        Compressor(
            threshold_db=-18,
            ratio=2.0,
            attack_ms=20,
            release_ms=250,
        ),
        Limiter(
            threshold_db=-1.0,
            release_ms=100,
        ),
    ])
    return board(y, sr)

def combine_wavs(wav_paths, output_path, gains_db=None):
    """Combine stems with LUFS normalization. No mastering applied."""
    if not wav_paths:
        raise ValueError("wav_paths must contain at least one file.")
    if gains_db is None:
        gains_db = [0.0] * len(wav_paths)
    if len(gains_db) != len(wav_paths):
        raise ValueError("gains_db must be the same length as wav_paths.")

    ref, target_sr = librosa.load(wav_paths[0], sr=None, mono=False)
    ref = ensure_2d(ref)
    target_channels = ref.shape[0]

    stems = []
    for path, gain_db in zip(wav_paths, gains_db):
        y, sr = librosa.load(path, sr=None, mono=False)
        y = ensure_2d(y)
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr, axis=-1)
        y = match_channels(y, target_channels)
        y = lufs_normalize(y, target_sr, target_lufs=-23.0)
        y = y * db_to_amp(gain_db)
        stems.append(y)

    max_len = max(s.shape[1] for s in stems)
    stems = [pad_to_length(s, max_len) for s in stems]
    mix = np.sum(stems, axis=0)
    mix = peak_normalize_with_headroom(mix, headroom_db=-6.0)

    sf.write(output_path, mix.T, target_sr)

def master_to_file(input_path, output_path):
    """Load a wav, apply mastering chain, save to output_path."""
    y, sr = librosa.load(input_path, sr=None, mono=False)
    y = ensure_2d(y)
    mastered = master_mix(y, sr)
    sf.write(output_path, mastered.T, sr)

if __name__ == '__main__':
    app.run(debug=True)