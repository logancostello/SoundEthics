from flask import Flask, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import demucs.api
import requests
import torch
import os
from flask_cors import CORS


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
    return "<p>Hello, World!</p>"

# endpoint: user uploads file that is stem-split
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # get stem type selection
        stem_type = request.form.get("stem")

        # make sure upload was valid
        if 'file' not in request.files:
             raise ValueError("No file uploaded!")
        
        file = request.files['file']
             
        if file.filename == '':
            raise ValueError("No file uploaded!")
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed.")
    
        # create directories for uploaded file, stem split file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(STEM_FOLDER, exist_ok=True)

        # upload the original file
        upload_filename = secure_filename(file.filename)
        upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
        file.save(upload_filepath)

        # read from uploaded place, call stem split
        stem_tensor = split_audio(upload_filepath, stem_type)

        # save stem split
        base_name = os.path.splitext(upload_filename)[0]  
        stem_filename = f"{base_name}_{stem_type}.wav"
        stem_filepath = os.path.join(app.config['STEM_FOLDER'], stem_filename)
        demucs.api.save_audio(stem_tensor, stem_filepath, samplerate=separator.samplerate)

        # finally, redirect user to stem split
        return {"url": url_for('download_stem', name=stem_filename, _external=True)}

    return """
    <h1>Upload & Split Audio</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file" accept="audio/*" required>
      <select name="stem" required>
        <option value="vocals">vocals</option>
        <option value="drums">drums</option>
        <option value="bass">bass</option>
        <option value="other">other</option>
      </select>
      <button type="submit">Upload</button>
    </form>
    """

# endpoint: user can download stem-split file
@app.route('/stems/<name>')
def download_stem(name):
    return send_from_directory(app.config["STEM_FOLDER"], name)

if __name__ == '__main__':
    app.run(debug=True)
