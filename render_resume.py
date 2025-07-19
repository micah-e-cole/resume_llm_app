# render_resume.py
'''
Author: Micah Braun
Date: 2025-07-19
Version: 2.0

Description:
Streamlit app to tailor resumes using a local LLM server (Ollama-compatible),
robustly handling streaming JSON responses and protecting fixed personal sections.
Outputs are saved as Markdown, PDF, and DOCX.
'''

import streamlit as st
import json
import requests
import os
from jinja2 import Environment, FileSystemLoader
import pypandoc
import difflib
import re
import shutil

# ---- Helper functions ----

def separate_protected_sections(data, protected_keys):
    protected = {k: data.get(k, []) for k in protected_keys}
    non_protected = {k: v for k, v in data.items() if k not in protected_keys}
    return non_protected, protected

def extract_json_from_text(text):
    """Clean response and extract JSON block"""
    text = re.sub(r'```json|```', '', text).strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decoding failed: {e}")
    raise ValueError("No valid JSON object found in response.")

def check_pandoc_engine():
    """Check if pdflatex is available for PDF conversion"""
    if not shutil.which('pdflatex'):
        st.warning("⚠️ 'pdflatex' not found. PDF export will fail. Install TeXLive or use --pdf-engine.")
        return False
    return True

# ---- Setup ----

os.makedirs('resumes', exist_ok=True)
os.makedirs('output', exist_ok=True)

st.set_page_config(page_title="Resume Tailoring App", layout="wide")
st.title("Resume Tailoring App (Robust Streaming Version)")

st.markdown("Paste a job description, select sections to update, and generate a tailored resume.\n"
            "**Personal details and fixed sections are protected from LLM exposure.**")

# ---- Input fields ----

focus_area = st.selectbox("Select Resume Focus Area", ["IT", "Software Development", "Security"])
organization = st.text_input("Organization Name", value="")
job_title = st.text_input("Job Title", value="")
job_desc = st.text_area("Paste Job Description", height=300, value="")
sections_to_update = st.multiselect(
    "Select sections to rewrite",
    ["summary", "skills", "experience", "projects", "technical-tools", "strengths"],
    default=["summary", "skills", "experience", "projects", "technical-tools", "strengths"]
)

if st.button("Generate Updated Resume"):
    if not (job_desc and organization and job_title):
        st.warning("Please fill in all fields.")
        st.stop()

    resume_file_path = f"resumes/{focus_area.lower().replace(' ', '_')}_resume.json"

    try:
        with open(resume_file_path) as f:
            resume_core = json.load(f)
    except FileNotFoundError:
        st.error(f"Resume file not found: {resume_file_path}")
        st.stop()

    try:
        with open('personal_info.json') as f:
            personal_info = json.load(f)
    except FileNotFoundError:
        st.error("personal_info.json not found.")
        st.stop()

    protected_keys = ["education", "certificates"]
    llm_input, protected_sections = separate_protected_sections(resume_core, protected_keys)

    prompt = (
        f"You are a resume assistant.\n"
        f"Here is my resume core data (excluding personal info and fixed sections): {json.dumps(llm_input)}\n"
        f"Here is the job description: {job_desc}\n"
        f"Please suggest updates ONLY for these sections: {', '.join(sections_to_update)}.\n"
        f"Important: Return ONLY a valid JSON object with no explanations or extra text."
    )

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'llama3:8b', 'prompt': prompt},
            stream=True,
            timeout=180
        )

        collected_responses = []
        for line in response.iter_lines():
            if line:
                try:
                    decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line
                    data = json.loads(decoded_line)
                    resp = data.get('response', '')
                    collected_responses.append(str(resp))
                except Exception:
                    continue  # skip lines that aren't JSON

        full_response_text = ''.join(collected_responses)
        
        st.markdown("### Raw LLM Combined Response")
        st.code(full_response_text)

        updated_json = extract_json_from_text(full_response_text)

    except Exception as e:
        st.error(f"❌ LLM call failed: {e}")
        st.stop()

    # Merge sections
    final_resume = {**resume_core, **updated_json, **protected_sections, **personal_info}

    first_name = personal_info.get('name', 'First Last').split()[0]
    last_name = personal_info.get('name', 'First Last').split()[-1]
    safe_org = organization.replace(' ', '_')
    safe_job = job_title.replace(' ', '_')
    safe_focus = focus_area.replace(' ', '')
    safe_name = f"{first_name}_{last_name}_{safe_focus}_{safe_job}"
    org_folder = os.path.join('output', safe_org)
    os.makedirs(org_folder, exist_ok=True)

    # Diff summary
    old_summary = resume_core.get('summary', '')
    new_summary = updated_json.get('summary', '')
    diff_summary = '\n'.join(difflib.unified_diff(old_summary.splitlines(), new_summary.splitlines(), lineterm=''))
    st.markdown("### Summary Diff")
    st.code(diff_summary or "No changes.")

    # Render Markdown
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('resume_template.md')
    rendered_md = template.render(final_resume)

    md_path = os.path.join(org_folder, f"{safe_name}.md")
    with open(md_path, 'w') as f:
        f.write(rendered_md)

    pdf_path = os.path.join(org_folder, f"{safe_name}.pdf")
    docx_path = os.path.join(org_folder, f"{safe_name}.docx")

    # Convert files
    if check_pandoc_engine():
        try:
            pypandoc.convert_file(md_path, 'pdf', outputfile=pdf_path)
        except Exception as e:
            st.warning(f"⚠️ PDF conversion failed: {e}")
    try:
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    except Exception as e:
        st.warning(f"⚠️ DOCX conversion failed: {e}")

    st.success(f"✅ Files saved to `{org_folder}`")

    # Download buttons
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            st.download_button("Download PDF", f, file_name=f"{safe_name}.pdf")
    if os.path.exists(docx_path):
        with open(docx_path, 'rb') as f:
            st.download_button("Download DOCX", f, file_name=f"{safe_name}.docx")

    st.markdown("---")
    st.markdown("**Tip:** Adjust model in script or template format in `resume_template.md` as needed.")