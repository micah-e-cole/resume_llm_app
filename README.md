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

5. Install Ollama (you will need to install according to your device(s) own requirements and bear in mind that not all GPUs are compatible with Ollama currently):
- Download from https://ollama.ai/download
- Run `ollama serve` in one terminal window

---

## Prepare your resume + focus areas

In the `resumes/` folder, create one JSON file **per focus area**, named (for example, but you can edit the names to be whatever the targets your are using):
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

These are the files the app will load automatically when you select the Focus Area dropdown.

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
output/<Organization>/<First_Last_FocusArea_JobTitle>.pdf
output/<Organization>/<First_Last_FocusArea_JobTitle>.docx
```

## Credits
Built with ChatGPT, Streamlit, Ollama, Pandoc, and Jinja2.

## Cheatsheet

### Change Model
In `render_resume.py`:

```python
json={'model': 'llama3:8b', 'prompt': prompt}
```
Replace `'llama3:8b'` with `'mistral:7b'`, `'nous-hermes-2-mixtral'`, etc.

---

### Edit LLM Prompt
In `render_resume.py`:

```python
prompt = f"""
You are a resume assistant.
Here is my resume (in JSON): {resume_data}
Here is the job description: {job_desc}
Please suggest updates ONLY for these sections: {', '.join(sections_to_update)}.
Return ONLY updated JSON.
"""
```
Change wording to guide style or focus (e.g., "rewrite summary in active voice").

---

### Customize Resume Layout
In `resume_template.md`:
- Change headers (`#`, `##`, `###`)
- Add bold (`**text**`), italics (`*text*`), or horizontal lines (`---`)
- Add new sections (certifications, awards, etc.)

---

### Customize Pandoc Output
In `render_resume.py`:
```python
pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
```
To apply custom DOCX style:
```python
pypandoc.convert_file(md_path, 'docx', outputfile=docx_path, extra_args=['--reference-doc=custom-style.docx'])
```
Ask me if you want a LaTeX template for fancy PDFs!

---

### Where Files Are Saved
- Folder: `output/<Organization>/`
- Filenames: `<First_Last_FocusArea_JobTitle>.md`, `.pdf`, `.docx`

Example:
```
output/Google/FirstName_LastName_FocusArea_JobTitle.pdf
```

---

## Tips 
1. Monitor system memory if running large tasks  
3. Use Activity Monitor (macOS), Task Manager (Windows), or top (Linux) to watch performance