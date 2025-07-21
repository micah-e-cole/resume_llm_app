# Configuring The Model
---
To test out the model once all of the dependencies have been installed, from one terminal run this command in the repository root folder:
`ollama serve`

If this command runs successfully, then in another terminal from the repository root folder run:
`streamlit run main.py`
If this runs successfully, you should see something like:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:<your-port>
  Network URL: http://<your-ip-address>
```

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