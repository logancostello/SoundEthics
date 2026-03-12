from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import torch.nn.functional as F
from scipy.io import wavfile
from flask_cors import CORS
from io import BytesIO
import numpy as np
import demucs.api
import requests
import torch
import crepe
import json
import os
from datetime import datetime

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

# convert crepe output to salience tensor with correct shape for JASCO
# number of target bins and frames found within JASCO documentation
def convert_crepe_to_jasco(activation, target_bins=53, target_frames=500):
    S = torch.from_numpy(activation).float()

    # activation initially (frequency, time), need to be (time, frequency)
    S = S.T

    # reduce number of pitch bins

    # add 2 dimensions to be input to the average pooling
    S = S.unsqueeze(0).unsqueeze(0)

    # conduct average polling
    S = F.adaptive_avg_pool2d(S, (target_bins, target_frames))

    # reduce dimensions again
    S = S.squeeze(0).squeeze(0)

    # resample time frames
    S = S.unsqueeze(0).unsqueeze(0)
    S = F.interpolate(S, size=(target_bins, target_frames), mode="bilinear", align_corners=False)
    S = S.squeeze(0).squeeze(0)  

    return S   

# given audio filepath, returns salience representation as PyTorch tensor
# NOTE: used ChatGPT to help generate this code
# TODO: might want to normalize/alter the salience matrix in some way to improve output
def get_salience(filename):
    # read in the audio file
    sr, audio = wavfile.read(filename)

    # predict time, frequency, confidence
    time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True, step_size=20)

    # if arrays don't have same length, raise error
    if (len(time) != len(frequency) or (len(frequency) != len(confidence))):
        raise ValueError("Crepe Array ouptut does not match!")    

    # convert ouptut to JASCO sizing
    jasco_size_tensor = convert_crepe_to_jasco(activation)

    return jasco_size_tensor

# send data to JASCO server
# consumes the JASCO URL, salience represention of melody (as tensor), path to .wav file, sample rate of drums, and a text prompt
def send_to_jasco(jasco_url, salience_tensor = None, drums_wav_path = None, drums_sample_rate = None, description=""):
    data = {}
    files = {}

    payload_meta = {
        "description": description
    }

    data["payload_json"] = json.dumps(payload_meta)
    
    if drums_sample_rate is not None:
        data["drums_sample_rate"] = str(drums_sample_rate)

    if drums_wav_path is not None:
        files["drums_wav"] = ("drums.wav", open(drums_wav_path, "rb"), "audio/wav")
    
    if salience_tensor is not None:
        salience_buffer = BytesIO()
        torch.save(salience_tensor, salience_buffer)
        salience_buffer.seek(0)
        files["melody_tensor"] = ("melody.pt", salience_buffer, "application/octet-stream")

    # make the request
    resp = requests.post(
        f"{jasco_url.rstrip('/')}/generate",
        files=files,
        data=data,
        timeout=600
    )

    # check for errors in response
    resp.raise_for_status()

    return resp

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

        # dictionary of filetypes and filepaths that will be used for JASCO generation
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
            split_filepaths[stem1] = stem_filepath

        # for stem_type in ['other', 'drums']:
        #     file = request.files.get(stem_type)

        #     # should only be able to submit one file
        #     if file and file.filename:
        #         if not allowed_file(file.filename):
        #             raise ValueError("File type not allowed.")
        
        #         # upload the original file to local folder
        #         upload_filename = secure_filename(file.filename)
        #         upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
        #         file.save(upload_filepath)

        #         # read original file from new folder, call stem split
        #         stem_tensor = split_audio(upload_filepath, stem_type)

        #         # save stem split to different local folder
        #         base_name = os.path.splitext(upload_filename)[0]  
        #         stem_filename = f"{base_name}_{stem_type}.wav"
        #         stem_filepath = os.path.join(app.config["STEM_FOLDER"], stem_filename)
        #         demucs.api.save_audio(stem_tensor, stem_filepath, samplerate=separator.samplerate)

        #         # save the stem type & filepath to use both for JASCO conditioning
        #         split_filepaths[stem_type] = stem_filepath

        # user should pass at least ONE song to generate on .. 
        # TODO: not sure if we should continue to enforce this ... what if user just wants to use description?
        if not split_filepaths: 
            raise ValueError("No conditioning files provided")

        salience_tensor = None
        drums_wav_path = None
        drums_sample_rate = None
        url = "http://127.0.0.1:8080"

        # fill in the data, if it exists
        for stem_type, filepath in split_filepaths.items():
            if stem_type == "melody":
                salience_tensor = get_salience(filepath)
            elif stem_type == "drums":
                drums_wav_path = filepath

        # make call to jasco service
        resp = send_to_jasco(url, salience_tensor, 
                      drums_wav_path, drums_sample_rate, description="upbeat hip-hop song with strong drums")
                          
        # save what's generated by writing to local folder
        wav_bytes = resp.content
        generated_filepath = os.path.join(app.config['GENERATED_FOLDER'], "generated.wav")
        sample_rate = int(resp.headers.get("sample_rate", 32000))

        with open(generated_filepath, "wb") as f:
            f.write(wav_bytes)

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

if __name__ == '__main__':
    app.run(debug=True)
