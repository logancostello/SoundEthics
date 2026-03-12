# Sound Ethics: Music Attribution

Conditioning generative music models on audio stems. 

To setup and run frontend: 
- create a virtual environment with Python version 3.9.25
- activate virtual environment
- ```pip install -r requirements.txt```
- ```cd frontend```
- ```npm run dev```

To setup and run backend: 
- create two virtual environments, each with Python version 3.9.25
- activate first virtual environment:
    - ```cd backend```
    - ```cd main_api```
    - ```pip install requirements.txt```
    - ```python app.py```
- activate second virtual environment:
    - ```cd backend```
    - ```cd jasco_api```
    - ```pip install requirements.txt```
    - ```python app.py```

**PLEASE NOTE** that JASCO model is gated, so you will have to get an access token from hugging face to use model. You can request that token [here](https://huggingface.co/facebook/jasco-chords-drums-melody-400M). Once you do so, please create a .venv file in root and add your token. Your .venv file will thus look like: 
```python
HF_TOKEN = YOUR_HUGGING_FACE_TOKEN
```
