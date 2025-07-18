### CheatSheet.md

````markdown
# 🛠️ Streamlit + LLM Resume App Cheat Sheet

## 🔧 Change Model
In `render_resume.py`:
```python
json={'model': 'llama3:8b', 'prompt': prompt}
```
Replace `'llama3:8b'` with `'mistral:7b'`, `'nous-hermes-2-mixtral'`, etc.

---

## 📝 Edit LLM Prompt
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

## 🖌️ Customize Resume Layout
In `resume_template.md`:
- Change headers (`#`, `##`, `###`)
- Add bold (`**text**`), italics (`*text*`), or horizontal lines (`---`)
- Add new sections (certifications, awards, etc.)

---

## 📄 Customize Pandoc Output
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

## 🗂️ Where Files Are Saved
- Folder: `output/<Organization>/`
- Filenames: `<First_Last_JobTitle>.md`, `.pdf`, `.docx`

Example:
```
output/Google/Micah_Braun_SoftwareEngineer.pdf
```

---

## 💡 Tips
✅ Stick to quantized models on Mac M2 (e.g., `llama3:8b.q4_K_M`)  
✅ Monitor system memory if running large tasks  
✅ Use Activity Monitor to watch performance

````
