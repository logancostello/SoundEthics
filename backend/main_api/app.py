from flask import Flask, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import numpy as np
import demucs.api
import os
import librosa
import soundfile as sf


'''
-----
SETUP 
-----
'''

app = Flask(__name__)
CORS(app)

# define locations for uploaded, stem-split, and generated content
UPLOAD_FOLDER = 'uploaded_content/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

STEM_FOLDER = "stem_content/"
app.config['STEM_FOLDER'] = STEM_FOLDER

GENERATED_FOLDER = "generated/"
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

# only allow certain files to be uploaded
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
ALLOWED_STEMS = {"drums", "melody"}

# initialize stem-splitter with default parameters
separator = demucs.api.Separator()

'''
----------------
HELPER FUNCTIONS
----------------
'''

# check if uploaded file type is allowed based on filename
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# split audio into stems
# consumes path to original audiofile, desired stem type (must be one of "drums", "bass", "vocals", "other")
# returns torch.Tensor representation of stem split
def split_audio(audio_path, desired_stem):
    if desired_stem not in ALLOWED_STEMS:
        raise ValueError("Desired Stem should be one of: drums, melody")
    
    origin, separated = separator.separate_audio_file(audio_path)

    for stem, source in separated.items():
        if stem == desired_stem: 
            return source
        # TODO: this is kind of wack but will work for now ... the problem is that 
        # Demucs will return "other" when we really mean "melody"
        elif stem == "other" and desired_stem == "melody":
            return source
    
    raise ValueError("Something went wrong when splitting audio!")

# given file and stem type, stem-split the file and save the output
# returns the filepath to the stem
def split_and_save(file, stem_type):
    # upload the original file to local folder
    upload_filename = secure_filename(file.filename)
    upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
    file.save(upload_filepath)

    # read original file from new folder, call stem split
    stem_tensor = split_audio(upload_filepath, stem_type)

    # save stem split to different local folder
    base_name = os.path.splitext(upload_filename)[0]  
    stem_filename = f"{base_name}_{stem_type}.wav"
    stem_filepath = os.path.join(app.config["STEM_FOLDER"], stem_filename)
    demucs.api.save_audio(stem_tensor, stem_filepath, samplerate=separator.samplerate)

    return stem_filepath
'''
---------
ENDPOINTS
---------
'''

# endpoint: home page 
@app.route("/")
def hello_world():
    return f"""<p>Hello, World!</p>
    <br>
    <a href={url_for("upload_file", _external=True)}>Upload File</a>
    """

# endpoint: user uploads file that is stem-split and used for generation
# TODO: url, description, and generated filename (generated.wav) are currently hard-coded
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # create directories for uploaded file, stem split file
        # do this only once
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(STEM_FOLDER, exist_ok=True)
        os.makedirs(GENERATED_FOLDER, exist_ok=True)

        split_filepaths = {}

        # TODO: restructure this whole thing, I think
        file1 = request.files.get('file1')
        stem1 = request.form.get("stem1")
        file2 = request.files.get('file2')
        stem2 = request.form.get("stem2")

        # raise error if no file provided
        if not file1 and not file2: 
            raise ValueError("No conditioning files provided")
        
        # process file1 if it exists
        if file1 and file1.filename:
            if not allowed_file(file1.filename):
                raise ValueError("File type not allowed.")
            if stem1 not in ALLOWED_STEMS:
                print(f"type: {stem1}")
                raise ValueError("Stem type not allowed.")
            stem_filepath = split_and_save(file1, stem1)
            split_filepaths[stem1] = stem_filepath

        # process file2 if it exists
        if file2 and file2.filename:
            if not allowed_file(file2.filename):
                raise ValueError("File type not allowed.")
            if stem2 not in ALLOWED_STEMS:
                raise ValueError("Stem type not allowed.")
            stem_filepath = split_and_save(file2, stem2)
            split_filepaths[stem2] = stem_filepath

        # user should pass at least ONE song to generate on .. 
        # TODO: not sure if we should continue to enforce this ... what if user just wants to use description?
        if not split_filepaths: 
            raise ValueError("No conditioning files provided")

        melody_wav_path = None
        drums_wav_path = None
        drums_sample_rate = None
        url = "http://127.0.0.1:8080"

        # fill in the data, if it exists
        for stem_type, filepath in split_filepaths.items():
            if stem_type == "melody":
                melody_wav_path = filepath
            elif stem_type == "drums":
                drums_wav_path = filepath

        generated_filepath = os.path.join(app.config['GENERATED_FOLDER'], "generated.wav")

        valid_files = []
        if drums_wav_path:
            valid_files.append(drums_wav_path)
            print("drums")

        if melody_wav_path:
            valid_files.append(melody_wav_path)
            print("melody")

        combine_wavs(
            valid_files,
            generated_filepath
        )

        # redirect to page with generated audio
        # NOTE: for testing locally (server-only)
        # return redirect(url_for('download_generated', name="generated.wav"))
        # NOTE: for testing with frontend
        return jsonify({"url": f"/generated/{os.path.basename(generated_filepath)}"})
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

# endpoint: user can download stem-split file
# can implement a similar structure for generated files
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

# endpoint: user can download generated file
# @app.route('/generated/<name>')
@app.route("/generated/<name>")
def download_generated(name):
    return send_from_directory(app.config["GENERATED_FOLDER"], name)



### LIBROSA

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


def combine_wavs(
    wav_paths: list[str],
    output_path: str,
    gains_db: list[float] = None,
    master_headroom_db: float = -1.0,
) -> None:
    """
    Mix any number of .wav files together and write to output_path.

    Args:
        wav_paths:           List of paths to input .wav files.
        output_path:         Path for the output mixed .wav file.
        gains_db:            Optional list of gain values (in dB) per file.
                             Must match length of wav_paths if provided.
                             Defaults to 0 dB for all stems.
        master_headroom_db:  Peak ceiling for the final mix (default -1.0 dB).
    """
    if not wav_paths:
        raise ValueError("wav_paths must contain at least one file.")

    if gains_db is None:
        gains_db = [0.0] * len(wav_paths)

    if len(gains_db) != len(wav_paths):
        raise ValueError("gains_db must be the same length as wav_paths.")

    # Load first file to establish reference sr and channels
    ref, target_sr = librosa.load(wav_paths[0], sr=None, mono=False)
    ref = ensure_2d(ref)
    target_channels = ref.shape[0]

    stems = []
    for path, gain_db in zip(wav_paths, gains_db):
        y, sr = librosa.load(path, sr=None, mono=False)
        y = ensure_2d(y)

        # Resample if needed
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr, axis=-1)

        # Match channels to reference
        y = match_channels(y, target_channels)

        # Apply gain
        y = y * db_to_amp(gain_db)

        stems.append(y)

    # Pad all stems to the longest length
    max_len = max(s.shape[1] for s in stems)
    stems = [pad_to_length(s, max_len) for s in stems]

    # Sum all stems
    mix = np.sum(stems, axis=0)

    # Peak normalize with headroom
    mix = peak_normalize_with_headroom(mix, headroom_db=master_headroom_db)

    # soundfile expects (samples, channels)
    sf.write(output_path, mix.T, target_sr)
    print(f"✅ Mixed {len(wav_paths)} stems into {output_path}")

if __name__ == '__main__':
    app.run(debug=True)

