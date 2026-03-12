# Sound Ethics: Music Attribution

Conditioning generative music models on audio stems. 

Model architecture based on SonyAI's Attribution-by-design. [Paper Link.](https://arxiv.org/abs/2510.08062)
 
To setup and run frontend: 
- create a virtual environment with Python version 3.9.25
- activate virtual environment
>>>>>>> 2f1c44b33032a79d19e1bc139a801b7fc75aad4b
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
