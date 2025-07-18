# Streamlit + LLM Resume Tailoring App

This project is a Streamlit web app that:
- Lets you select a resume focus area (e.g., IT, Software Development, Security)
- Uses a local LLM (Ollama) to tailor resume sections based on a pasted job description
- Generates updated resumes in PDF and DOCX formats using Pandoc

## Setup
### Folder Structure
```resume_project/
├── render_resume.py                  # Main Streamlit app script
├── resume_template.md                # Jinja2 Markdown template for rendering resumes
├── requirements.txt                  # Python dependencies
├── README.md                         # Project README for GitHub
├── Makefile (optional)               # Optional CLI helper for common commands
├── resumes/                          # Folder holding base resumes for each focus area
│   ├── it_resume.json                # Base resume for IT roles
│   ├── software_development_resume.json  # Base resume for Software Development roles
│   └── security_resume.json          # Base resume for Security roles
├── cheatSheet.md                     # Tips on customizing models, prompts, templates, etc.
└── output/                           # Folder where generated files are saved
    └── <Organization>/               # Folder for each organization/job application (e.g., Google)
        ├── First_Last_FocusArea_JobTitle.md    # Rendered Markdown resume
        ├── First_Last_FocusArea_JobTitle.pdf   # Generated PDF resume
        └── First_Last_FocusArea_JobTitle.docx  # Generated DOCX resume
```
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

---

## Prepare your resume + focus areas

In the `resumes/` folder, create one JSON file **per focus area**, named:
```
it_resume.json
software_development_resume.json
security_resume.json
```

Each file should contain the base resume for that career path, e.g.,:

```
resumes/it_resume.json
resumes/software_development_resume.json
resumes/security_resume.json
```

✅ These are the files the app will load automatically when you select the Focus Area dropdown.

---

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