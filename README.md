# Sound Ethics: Music Attribution

This application is created in collaboration with Sound Ethics, which is an organization that develops and advocates for ethical artificial intelligence (AI). Our framework allows users maximum creative control when generating music and gives proper credit to the original artists. Users can upload and isolate specific components of audio clips to create an output. These components include the drums, piano, guitar and bass. Additionally, users can provide a text prompt and specify certain audio features, such as BPM, duration, and key. 
 
The backbone of our implementation is the open-source [ACE-Step](https://ace-step.github.io/) music generation model. We also utilize [Demucs](https://github.com/adefossez/demucs) for stem isolation and [Librosa](https://librosa.org/) for audio processing.

You can follow the **Setup Instructions** to start generating music! Or, you can read more about the project's motivation, development, and outcomes in our paper and reserach poster, which are both contained in the `/docs` folder.

## Project Structure
```text
root/
├── backend/               # Backend application code
│   ├── .gitignore         # Files hidden and ignored by Git tracking
│   ├── app.py             # Application Script
│   ├── requirements.txt   # External libraries used for backend
├── frontend/              # Frontend application code
│   ├── src/               # Source code files
│   ├── .gitignore         # Files hidden and ignored by Git tracking
│   ├── package.json       # Core metadata document
│   ├── index.html         # Homepage
│   ├── vite.config.js     # Central configuration for Vite
│   ├── requirements.txt   # External libraries used for frontend
├── docs/                  # Project documentation: research poster and report
├── .gitignore             # Files hidden and ignored by Git tracking
├── README.md              # Project overview
```

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

- **BPM (Beats Per Minute)**: Speed of musical composition.
- **Duration**: Length of output audio in seconds.
- **Inference Steps**: Number of denoising steps. More steps means higher-quality output.
- **Seed**: Number used to control randomness. Use the same seed multiple times to generate the same output.
- **Cover Strength**: How similar output audio is to input audio.
- **Guidance Scale**: How similar output audio is to input prompt.
- **Key**: Musical key.
- **Thinking**: Enables ACE-Step's LLM to analyze input and structure coherent output. **We recommend leaving this on for best results!**