# Sound Ethics: Music Attribution

Conditioning generative music models on audio stems. 
 
To setup and run frontend: 
- create a virtual environment with Python version 3.9.25
- activate virtual environment
- ```cd frontend```
- ```pip install -r requirements.txt```
- ```npm run dev```

To setup and run backend: 
- create a virtual environment with Python version 3.9.25
- activate first virtual environment:
- ```cd backend```
- ```pip install -r requirements.txt```
- ```python app.py```

To setup and run ACE:
Install uv (if you don't have it)
- ```curl -LsSf https://astral.sh/uv/install.sh | sh```

Install ACE
- ```git clone https://github.com/ACE-Step/ACE-Step-1.5.git```
- ```cd ACE-Step-1.5```
- ```uv sync```

Run ACE
- ```ACESTEP_INIT_LLM=false uv run acestep-api```