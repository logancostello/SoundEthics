from flask import Flask, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import demucs.api
import requests
import torch
import os

app = Flask(__name__)

# define location for uploaded content
UPLOAD_FOLDER = 'uploaded_content/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# only allow certain files to be uploaded
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

'''
--- HELPER FUNCTIONS ---
'''

# check if uploaded file type is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


'''
-- ENDPOINTS --
'''

# endpoint: home page 
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# endpoint: user can upload file
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # create folder if it doesn't already exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# endpoint: user can download file
# TODO: this assumes that they already know the name of the file they are looking for though, right? 
@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


# TODO!!
# endpoint: split the file!!
@app.route("/api/stem-split")
def split_stems():
    # for now, just pass in some local file .. can make bigger changes latear
    print("hello brother")
    # TODO: split some stems and what not .. make sure we have everything created and installed correctly

if __name__ == '__main__':
    app.run(debug=True)


'''
- tutorial for uploading content came from here: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
- 
'''