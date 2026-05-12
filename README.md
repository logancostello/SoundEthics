# Sound Ethics: Music Attribution

Conditioning generative music models on audio stems. 
 
To setup and run frontend: 
- create a virtual environment with Python version 3.9.25
- activate virtual environment
- ```cd frontend```
- ```pip install -r requirements.txt```
- ```npm run dev```

To setup and run backend: 
- create a .env file in the backend directory
- put this in the env file: export ACESTEP_URL="your_api_path_here"
- create a virtual environment with Python version 3.9.25
- activate first virtual environment:
- ```cd backend```
- ```pip install -r requirements.txt```
- ```python app.py```

> **PLEASE NOTE** that we are using a cloud-hosted verion of [Ace-Step 1.5](https://github.com/ace-step/ACE-Step-1.5). You will need to have access to that URL to use this application. Once you gain access, please create a .venv file in root and add the URL. Your .venv file will thus look like: 
```python
ACESTEP_URL = CLOUD_HOSTED_URL
```

