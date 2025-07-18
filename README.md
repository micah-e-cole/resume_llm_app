# Streamlit + LLM Resume Tailoring App

This project is a Streamlit web app that:
- Uploads your resume JSON and job description
- Uses a local LLM (Ollama) to tailor resume sections
- Generates updated resumes in PDF and DOCX formats via Pandoc

## Setup

1. Clone this repo and navigate into the folder:
```bash
git clone <repo-url>
cd resume_project
```

2. Create virtual environment and activate:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Pandoc:
```bash
brew install pandoc
```

5. Install Ollama (Mac M2 recommended):
- Download from https://ollama.ai/download
- Run `ollama serve` in one terminal window

## Run the app
```bash
streamlit run render_resume.py
```
Visit [http://localhost:8501](http://localhost:8501) in your browser.

## How to customize
- See `CheatSheet.md` for model, prompt, template, and Pandoc tips.
- Edit `resume_template.md` for Markdown layout.
- Copy resume_sample.json to resume.json and fill in your personal data locally.
- Add or update example `resume.json`.

## Outputs
Generated files are saved to:
```
output/<Organization>/<First_Last_JobTitle>.pdf
output/<Organization>/<First_Last_JobTitle>.docx
```

## Credits
Built with ChatGPT, Streamlit, Ollama, Pandoc, and Jinja2.
````