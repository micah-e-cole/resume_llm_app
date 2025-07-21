'''
Author: Micah Braun
Date: 2025-07-19
Version: 1.1

Description:
Streamlit app to tailor resumes using a local LLM server (Ollama: llama3:8b),
handling streaming JSON responses and protecting fixed personal sections.
Outputs are saved as Markdown, PDF, and DOCX.

Improvements:
- Robust LLM stream handling
- JSON cleaning and extraction fixes
- ATS-optimized LLM prompting
- Keyword extraction + match check
'''

import streamlit as st
import json
import requests
import os
from jinja2 import Environment, FileSystemLoader
from styler import apply_styles_to_docx
import pypandoc
import difflib
import re
import shutil

# ---- Helper functions ----

def separate_protected_sections(data, protected_keys):
    protected = {k: data.get(k, []) for k in protected_keys}
    non_protected = {k: v for k, v in data.items() if k not in protected_keys}
    return non_protected, protected

def clean_json_like_text(text):
    """Clean LLM output to be valid JSON"""
    text = re.sub(r'```json|```', '', text).strip()
    text = re.sub(r"'(\w+)':", r'"\1":', text)  # keys: 'key': → "key":
    text = re.sub(r':\s*\'([^\']*)\'', r': "\1"', text)  # string values: : 'value' → : "value"
    return text

def extract_json_from_text(text):
    """Extract and clean JSON block from LLM response"""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_block = match.group(0)
        cleaned_json = clean_json_like_text(json_block)
        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decoding failed after cleaning: {e}")
    raise ValueError("No valid JSON object found in response.")

def extract_keywords(text, top_n=15):
    """Extract top keywords (simple frequency-based) from text"""
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = set([
        'the', 'and', 'for', 'with', 'you', 'are', 'this', 'that', 'from', 'they',
        'their', 'your', 'will', 'have', 'has', 'but', 'not', 'all', 'any', 'can', 'may', 'such',
        'a', 'an', 'of', 'in', 'on', 'at', 'by', 'to', 'is', 'it', 'be', 'as', 'or', 'if'
    ])
    filtered = [word for word in words if word not in stopwords and len(word) > 2]
    freq = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_keywords[:top_n]]

def check_pandoc_engine():
    """Check if pdflatex is available for PDF conversion"""
    if not shutil.which('pdflatex'):
        st.warning("'pdflatex' not found. PDF export will fail. Install TeXLive or use --pdf-engine.")
        return False
    return True

# ---- Setup ----

os.makedirs('resumes', exist_ok=True)
os.makedirs('output', exist_ok=True)

st.set_page_config(page_title="Resume Tailoring App", layout="wide")
st.title("Resume Tailoring App")

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
        "You are an expert resume assistant specialized in writing ATS-optimized resumes that rank in the top 10% of job applicants.\n\n"
        "TASK:\n"
        "- Rewrite the provided resume sections using the job description below.\n"
        "- Incorporate relevant industry keywords, accomplishments, and outcome-focused language.\n"
        "- Use active, impact-focused phrasing aligned with best practices for ATS systems.\n"
        "- Avoid generic fluff; focus on specific, measurable, or verifiable improvements.\n"
        "- Ensure output is a clean, valid JSON object with no explanations, comments, or markdown.\n"
        "- Use ONLY double quotes around keys and string values.\n"
        "- Do NOT wrap the output in ```json or other code fences.\n\n"
        f"Here is my resume core data (excluding personal info and fixed sections): {json.dumps(llm_input)}\n"
        f"Here is the job description: {job_desc}\n"
        f"Please suggest updates ONLY for these sections: {', '.join(sections_to_update)}.\n"
        "Important: Return ONLY a valid JSON object using double quotes, no single quotes, no explanations, no markdown code fences."
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
                decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line
                collected_responses.append(decoded_line)

        full_response_text = ''.join(collected_responses)

        st.markdown("### Debug: Collected LLM Raw Response")
        st.code(full_response_text)

        updated_json = extract_json_from_text(full_response_text)

    except Exception as e:
        st.error(f"LLM call failed: {e}")
        st.stop()

    # Keyword check
    job_keywords = extract_keywords(job_desc, top_n=15)
    resume_text = json.dumps(updated_json).lower()
    matched_keywords = [kw for kw in job_keywords if kw in resume_text]

    st.markdown("### Keyword Match Check")
    st.write(f"**Top job description keywords:** {', '.join(job_keywords)}")
    st.write(f"**Matched in updated resume:** {', '.join(matched_keywords) if matched_keywords else 'None'}")

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
            st.warning(f"PDF conversion failed: {e}")
    try:
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    except Exception as e:
        st.warning(f"DOCX conversion failed: {e}")

    st.success(f"Files saved to `{org_folder}`")

    # Apply styling
    styled_docx_path = os.path.join(org_folder, f"{safe_name}_styled.docx")
    try:
        apply_styles_to_docx(docx_path, 'styles.json', styled_docx_path)
    except Exception as e:
        st.warning(f"Styling DOCX failed: {e}")

    # Download buttons
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            st.download_button("Download PDF", f, file_name=f"{safe_name}.pdf")
    if os.path.exists(styled_docx_path):
        with open(styled_docx_path, 'rb') as f:
            st.download_button("Download Styled DOCX", f, file_name=f"{safe_name}_styled.docx")

    st.markdown("---")
    st.markdown("**Tip:** Adjust model in script or template format in `resume_template.md` as needed.")
