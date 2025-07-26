# Streamlit + LLM Resume Tailoring App

This project is a Streamlit web app that:
- Lets you select a resume focus area (e.g., IT, Software Development, Security)
- Uses a local LLM (Ollama) to tailor resume sections based on a pasted job description
- Generates updated resumes in PDF and DOCX formats using Pandoc

## Setup
### Folder Structure
```
resume_project/
├── main.py 
├── _helpers/
│   ├── file_utils.py                     # Contains helper functions for handling text functions in main.py
│   ├── llm_client.py                     # Contains the helper functions for interacting with and prompting the LLM
│   ├── constants.py                      # Contains the constants used throughout the files
│   └── styler.py                         # Contains the .DOCX file formatting that Pandoc will use in .DOCX conversion
├── resume_template.md                    # Jinja2 Markdown template for rendering resumes
├── requirements.txt                      # Python dependencies
├── README.md                             # Project README for GitHub
├── my-reference.docx                     # Reference template for .docx file types (customize font/styles)
├── styles.json                           # Style formatting to be used by Python's python-docx
├── Makefile (optional)                   # Optional CLI helper for common commands
├── resumes/                              # Folder holding base resumes for each focus area (customize)
│   ├── it_resume.json                    # Base resumes for IT roles
│   ├── software_development_resume.json  # Base resume for Software Development roles
│   └── security_resume.json              # Base resume for Security roles
└── output/                                     # Folder where generated files are saved
    └── <Organization>/                         # Folder for each organization/job application (e.g., Google)
        ├── First_Last_FocusArea_JobTitle.md    # Rendered Markdown resume
        ├── First_Last_FocusArea_JobTitle.pdf   # Generated PDF resume
        └── First_Last_FocusArea_JobTitle.docx  # Generated DOCX resume
```
### Technical Requirements
- Python Environment 3.8 - 3.12 recommended (this was written with 3.11.5)
- Python packages (required packages can be found in the requirements.txt file)
- Local LLM backend: Ollama server running locally on port 11434 (model: llama3:8b)
- Pandoc
- If using macOS: pdflatex for .PDF conversion with Pandoc
- At the time of writing, this has only been tested on macOS YMMV
- *Minimum* hardware recommendations: 4-core CPU, 8GB RAM (basic)

1. Clone the repository and navigate into the folder:

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

---

## Other Helpful Information
For more information on how to change elements of this for your own use(s), head over to the [Configuration page](configuring_model.md).

## Credits
Built with ChatGPT, Streamlit, Ollama, Pandoc, and Jinja2.