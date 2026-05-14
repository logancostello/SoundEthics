# Sound Ethics: Music Attribution

This framework is designed to give users maximum creative control when generating music. 

The backbone of our implementation is the [ACE-Step](https://ace-step.github.io/) music generation model.

Follow the Setup Instructions to start generating music! :D

You can read more about the project's motivation, development, and outcomes in our paper.

Or, you could look over our research poster.

Happy creating!

## Setup Instructions
To setup and run frontend: 
- create a virtual environment with Python version 3.9.25
- activate virtual environment
- ```cd frontend```
- ```pip install -r requirements.txt```
- ```npm run dev```

To setup and run backend: 
- create a .env file in the backend directory
- put this in the env file: export ACESTEP_URL="your_api_path_here"
- create another virtual environment with Python version 3.9.25
- activate this virtual environment
- ```cd backend```
- ```pip install -r requirements.txt```
- ```python app.py```

## Parameter Descriptions

A short description of each model parameter.

- BPM (Beats Per Minute): Speed of musical composition.
- Duration: Length of output audio in seconds.
- Inference Steps: Number of denoising steps. More steps means higher-quality output.
- Seed: Number used to control randomness. Use the same seed multiple times to generate the same output.
- Cover Strength: How similar output audio is to input audio.
- Key: Musical key.
- Thinking: Enables ACE-Step's LLM to analyze input and structure coherent output. **We recommend leaving this on for best results!**