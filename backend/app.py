from flask import Flask, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import demucs.api
import requests
import torch
import os
from flask_cors import CORS
from datetime import datetime


'''
-- NOTES / LINKS ---
tutorial for uploading content came from here: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
'''

'''
--- SETUP ---
'''

app = Flask(__name__)
CORS(app)              

# define location for uploaded content
UPLOAD_FOLDER = 'uploaded_content/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# define location for stem content
STEM_FOLDER = "stem_content/"
app.config['STEM_FOLDER'] = STEM_FOLDER

# only allow certain files to be uploaded
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
ALLOWED_STEMS = {"drums", "bass", "vocals", "other"}

# initialize stem-splitter with default parameters
separator = demucs.api.Separator()

'''
--- HELPER FUNCTIONS ---
'''

# check if uploaded file type is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

'''
consumes path to original audiofile, desired stem type (must be one of "drums", "bass", "vocals", "other")
returns torch.Tensor representation of stem split
'''
def split_audio(audio_path, desired_stem):
    if desired_stem not in ALLOWED_STEMS:
        raise ValueError("Desired Stem should be one of: drums, bass, vocals, other")
    
    origin, separated = separator.separate_audio_file(audio_path)

    for stem, source in separated.items():
        if stem == desired_stem: 
            return source
    
    raise ValueError("Something went wrong when splitting audio!")

'''
-- ENDPOINTS --
'''

# endpoint: home page 
@app.route("/")
def hello_world():
    return f"""<p>Hello, World!</p>
    <br>
    <a href={url_for("upload_file", _external=True)}>Upload File</a>
    """

# endpoint: user uploads file that is stem-split
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # get stem type selection
        # stem_type = request.form.get("stem")

        # make sure upload was valid
        if 'other' not in request.files and 'drums' not in request.files:
            raise ValueError("No file uploaded!")

        # create directories for uploaded file, stem split file
        # do this only once
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(STEM_FOLDER, exist_ok=True)

        folder_name = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        stem_folder_path = os.path.join(app.config["STEM_FOLDER"], folder_name)
        
        os.makedirs(stem_folder_path, exist_ok=True)

        for stem_type in ['other', 'drums']:
            file = request.files[stem_type]

            if file.filename == '':
                #raise ValueError("No file uploaded!")
                # we want to allow for missing files as long as there's at least one
                continue

            if not allowed_file(file.filename):
                raise ValueError("File type not allowed.")

            # upload the original file
            upload_filename = secure_filename(file.filename)
            upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
            file.save(upload_filepath)

            # read from uploaded place, call stem split
            stem_tensor = split_audio(upload_filepath, stem_type)

            # save stem split
            base_name = os.path.splitext(upload_filename)[0]  
            stem_filename = f"{base_name}_{stem_type}.wav"
            stem_filepath = os.path.join(stem_folder_path, stem_filename)
            demucs.api.save_audio(stem_tensor, stem_filepath, samplerate=separator.samplerate)

        # finally, redirect user to stem split
        return {"url": url_for('download_stems', folder=folder_name, _external=True)}

    return """
    <h1>Upload & Split Audio</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="other" accept="audio/*" required>
      <select name="stem" required>
        <option value="other">other</option>
      </select>
      <br>
      <input type="file" name="drums" accept="audio/*" required>
      <select name="stem" required>
        <option value="drums">drums</option>
      </select>
      <br>
      <button type="submit">Upload</button>
    </form>
    """

# endpoint: user can download stem-split file
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

if __name__ == '__main__':
    app.run(debug=True)
