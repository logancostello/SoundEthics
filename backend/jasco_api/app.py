from flask import Flask, request, request, jsonify, send_file
from werkzeug.utils import secure_filename
from audiocraft.models import JASCO
from huggingface_hub import login
from dotenv import load_dotenv
from flask_cors import CORS
from io import BytesIO
import torchaudio
import requests
import torch
import os
import json

'''
-----
SETUP 
-----
'''

app = Flask(__name__)
CORS(app)

# log into hugging face since the model is gated
# NOTE: this will require generating your own token and saving in .env file at root
load_dotenv()
token = os.getenv("HF_TOKEN")
print(token)
if token:
    login(token=token)

# load the required JASCO stuff 
CHORDS_MAPPING = os.path.abspath("assets/chord_to_index_mapping.pkl")
model = JASCO.get_pretrained("facebook/jasco-chords-drums-melody-400M", chords_mapping_path=CHORDS_MAPPING)

'''
---------
ENDPOINTS
---------
'''

# endpoint: home page 
# TODO: honestly can just remove, not going to use at all
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# endpoint: generate song with JASCO, using payload from main API
# TODO: figure out how to use dynamic sample rate & filename
@app.route("/generate", methods=["POST"])
def generate():
    # extract information from data playload
    payload_json = request.form.get("payload_json")
    payload = json.loads(payload_json)

    description = payload.get("description")

    sr_field = request.form.get("drums_sample_rate")

    if sr_field:
        drums_sample_rate = int(sr_field)
    else: 
        drums_sample_rate = None

    # read files: drums and melody
    drums_wav_file = request.files.get("drums_wav")       
    melody_tensor_file = request.files.get("melody_tensor") 

    # reconstruct drums
    drums_wav = None
    drums_sample_rate = None
    if drums_wav_file:
        wav_bytes = drums_wav_file.read()
        wav_buf = BytesIO(wav_bytes)
        try:
            drums_wav, drums_sample_rate = torchaudio.load(wav_buf)
        except RuntimeError as e:
            return jsonify({"Error while loading .wav file": f"{e}"}), 400

    # reconstruct melody
    melody_salience_tensor = None
    if melody_tensor_file:
        tensor_buf = BytesIO(melody_tensor_file.read())
        tensor_buf.seek(0)
        melody_salience_tensor = torch.load(tensor_buf, map_location="cpu")
        # reshape in accordance with original JASCO demo notebook
        melody_salience_tensor = melody_salience_tensor
        print(melody_salience_tensor.shape)

    # make call to JASCO API
    try:
        # set generation params, like in JASCO demo
        model.set_generation_params(
            cfg_coef_all=1.5,
            cfg_coef_txt=2.5,
            euler=True,
            euler_steps=50
        )

        # TODO: remove logging before push to prod ... 
        print("WE HAVE SET MODEL PARAMS")

        # NOTE: have to convert descriptions to list for type compatability
        output = model.generate_music(descriptions=[description],
                                      drums_wav = drums_wav, 
                                      drums_sample_rate=drums_sample_rate,
                                      melody_salience_matrix = melody_salience_tensor,
                                      progress=False)

        print("WE WERE ABLE TO GENERATE OUTPUT")

        # create path to save audio
        out_path = "outputs"
        os.makedirs(out_path, exist_ok=True)
        saved_file = os.path.join(out_path, "generated.wav")

        # change shape of output audio
        wav = output
        wav = wav.squeeze(0)
        
        # set sample rate
        sample_rate = 32000

        # save output audio
        torchaudio.save(saved_file, wav, sample_rate)
    
        # send back to main API
        response = send_file(
            saved_file, 
            mimetype="audio/wav",
            as_attachment=True,
            download_name="generated.wav",
        )

        response.headers["sample_rate"] = str(sample_rate)
        return response
    
    except Exception as e:
        return jsonify({
        "error": "Error while generating with JASCO",
        "details": str(e)
    }), 500

if __name__ == '__main__':
    app.run(port=8080, debug=False, use_reloader=False)