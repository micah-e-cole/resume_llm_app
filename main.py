'''Author: Micah Braun
Date: 2025-07-19
Version: 1.2

Description:
Streamlit app to tailor resumes using a local LLM server (Ollama: llama3:8b),
handling streaming JSON responses and protecting fixed personal sections.
Outputs are saved as Markdown, PDF, and DOCX.

Improvements:
- LLM stream handling
- JSON cleaning and extraction fixes
- ATS-optimized LLM prompting
- Keyword extraction + match check
- DOCX styling with custom styles


'''
# import necessary libraries
import streamlit as st
import json
import os
from llm_client import get_updated_resume_json, extract_keywords, check_pandoc_engine
from file_utils import load_json, save_file, convert_to_pdf, convert_to_docx, apply_docx_styles, generate_diff
from constants import PROTECTED_KEYS

# ---- Setup ----
os.makedirs('resumes', exist_ok=True)
os.makedirs('output', exist_ok=True)

st.set_page_config(page_title="Resume Tailoring App", layout="wide")
st.title("Resume Tailoring App")

st.markdown("""
Paste a job description, select sections to update, and generate a tailored resume.

**Personal details and fixed sections are protected from LLM exposure.**
""")

# ---- Input Fields ----
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

    with st.spinner("Loading resume and personal info..."):
        resume_file = f"resumes/{focus_area.lower().replace(' ', '_')}_resume.json"
        personal_file = "personal_info.json"
        resume_core = load_json(resume_file)
        personal_info = load_json(personal_file)

    with st.spinner("Calling LLM to generate updated resume..."):
        updated_json, raw_response = get_updated_resume_json(
            resume_core, job_desc, sections_to_update, PROTECTED_KEYS
        )

    # Display raw LLM response for debugging
    st.markdown("### Debug: Collected LLM Raw Response")
    st.code(raw_response)

    with st.spinner("Extracting and matching job description keywords..."):
        job_keywords = extract_keywords(job_desc, top_n=15)
        resume_text = json.dumps(updated_json).lower()
        matched_keywords = [kw for kw in job_keywords if kw in resume_text]

    st.markdown("### Keyword Match Check")
    st.write(f"**Top job description keywords:** {', '.join(job_keywords)}")
    st.write(f"**Matched in updated resume:** {', '.join(matched_keywords) or 'None'}")

    # Merge sections
    final_resume = {**resume_core, **updated_json, **personal_info}

    # Create safe filenames
    first_name = personal_info.get('name', 'First Last').split()[0]
    last_name = personal_info.get('name', 'First Last').split()[-1]
    safe_org = organization.replace(' ', '_')
    safe_job = job_title.replace(' ', '_')
    safe_focus = focus_area.replace(' ', '')
    safe_name = f"{first_name}_{last_name}_{safe_focus}_{safe_job}"
    org_folder = os.path.join('output', safe_org)
    os.makedirs(org_folder, exist_ok=True)

    with st.spinner("Generating diff summary..."):
        diff_summary = generate_diff(resume_core.get('summary', ''), updated_json.get('summary', ''))

    st.markdown("### Summary Diff")
    st.code(diff_summary or "No changes.")

    with st.spinner("Rendering resume as Markdown..."):
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('resume_template.md')
        rendered_md = template.render(final_resume)
        md_path = os.path.join(org_folder, f"{safe_name}.md")
        save_file(md_path, rendered_md)

    pdf_path, docx_path, styled_docx_path = None, None, None

    with st.spinner("Converting to PDF and DOCX..."):
        if check_pandoc_engine():
            pdf_path = convert_to_pdf(md_path, org_folder, safe_name)
        docx_path = convert_to_docx(md_path, org_folder, safe_name)

    with st.spinner("Applying styles to DOCX..."):
        styled_docx_path = apply_docx_styles(docx_path, 'styles.json', org_folder, safe_name)

    st.success(f"Files saved to `{org_folder}`")

    # Download buttons
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            st.download_button("Download PDF", f, file_name=f"{safe_name}.pdf")
    if styled_docx_path and os.path.exists(styled_docx_path):
        with open(styled_docx_path, 'rb') as f:
            st.download_button("Download Styled DOCX", f, file_name=f"{safe_name}_styled.docx")

    st.markdown("---")
    st.markdown("**Tip:** Adjust model or template format in `resume_template.md` as needed.")
# ---- End of main.py ----
