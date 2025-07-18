
# 📦 **roject Folder Architecture (with Organization + Filename Naming)**

```
resume_project/
├── render_resume.py              # Main Streamlit app script
├── resume_template.md            # Jinja2 Markdown template
├── resume.json                   # Example resume JSON file
├── requirements.txt              # Python dependencies
├── README.md                     # Project README for GitHub
├── Makefile (optional)           # Optional CLI helper
└── output/                       # Folder where generated files are saved
    └── <Organization>/           # Folder for each organization/job application (e.g., Google)
        └── First_Last_JobTitle.md     # Rendered Markdown resume
        └── First_Last_JobTitle.pdf    # Generated PDF resume
        └── First_Last_JobTitle.docx   # Generated DOCX resume
```

**Example**
```
output/Google/Micah_Braun_SoftwareEngineer.pdf
output/Google/Micah_Braun_SoftwareEngineer.docx
```

 **In the Python script**, you’ll need to:
- Extract organization name from job description input (could be an extra text field).
- Generate filename like `First_Last_JobTitle` (sanitize spaces/special chars).
- Save files inside `output/<Organization>/`.

**Why?**
- Organizes outputs per job application.
- Makes it easy to track multiple tailored resumes.
- Great for showing off organized, scalable solutions in your portfolio.

