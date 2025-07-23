# main.py
'''
Author: Micah Braun
Date: 2025-07-19
Version: 1.2

Description:
Streamlit app to tailor resumes using a local LLM server (Ollama: llama3:8b),
handling streaming JSON responses and protecting fixed personal sections.
Outputs are saved as Markdown, PDF, and DOCX.

Files included:
- main.py: Streamlit app logic
- llm_client.py: LLM interaction and JSON handling
- constants.py: Application constants
- styler.py: DOCX styling functions
- file_utils.py: File handling utilities
'''

import streamlit as st
import nltk
import json
import os

from _helpers.llm_client import get_updated_resume_json, check_pandoc_engine
from _helpers.file_utils import load_json, save_file, convert_to_pdf, convert_to_docx, apply_docx_styles, generate_diff
from _helpers.constants import PROTECTED_KEYS
from _helpers.lemmatize import match_keywords_with_synonyms, rank_matched_keywords_by_tfidf, ensure_nltk_resources
from _helpers.lemmatize import match_keywords_with_synonyms, rank_matched_keywords_by_tfidf, ensure_nltk_resources

ensure_nltk_resources()  # Make sure this runs early in your app

# ---- Ensure folders ----
os.makedirs('resumes', exist_ok=True)
os.makedirs('output', exist_ok=True)

# ---- Ensure NLTK resources once per session ----
if 'nltk_ready' not in st.session_state:
    st.session_state['nltk_ready'] = False

if not st.session_state['nltk_ready']:
    with st.spinner("Checking and downloading NLTK resources... (this only runs once per session)"):
        try:
            from _helpers.lemmatize import ensure_nltk_resources
            ensure_nltk_resources()
            st.session_state['nltk_ready'] = True
            st.success("NLTK resources are ready!")
        except Exception as e:
            st.error(f"Error ensuring NLTK resources: {e}")
            st.stop()


# ---- Streamlit setup ----
st.set_page_config(page_title="Resume Tailoring App", layout="wide")
st.title("Resume Tailoring App")

st.markdown("""
Paste a job description, select sections to update, and generate a tailored resume.

**Personal details and fixed sections are protected from LLM exposure.**
""")

# ---- Inputs ----
focus_area = st.selectbox("Select Resume Focus Area", ["IT", "Software Development", "Security"])
organization = st.text_input("Organization Name", value="")
job_title = st.text_input("Job Title", value="")
job_desc = st.text_area("Paste Job Description", height=300, value="")

sections_to_update = st.multiselect(
    "Select sections to rewrite",
    ["summary", "skills", "experience", "projects", "technical-tools", "strengths"],
    default=["summary", "skills", "experience"]
)

if st.button("Generate Updated Resume"):
    if not (job_desc and organization and job_title):
        st.warning("Please fill in all fields.")
        st.stop()

    # ---- Load files ----
    with st.spinner("Loading resume and personal info..."):
        resume_file = f"resumes/{focus_area.lower().replace(' ', '_')}_resume.json"
        personal_file = "personal_info.json"
        resume_core = load_json(resume_file)
        personal_info = load_json(personal_file)

    # ---- Analyze keywords ----
    with st.spinner("Analyzing job description and resume for keywords..."):
        resume_text = json.dumps(resume_core)
        matched_keywords = match_keywords_with_synonyms(job_desc, resume_text)
        ranked_keywords = rank_matched_keywords_by_tfidf(matched_keywords, [job_desc, resume_text])

    st.markdown("### Enhanced Keyword Match Check")
    if matched_keywords:
        st.write(f"**Matched (lemmatized + synonyms):** {', '.join(matched_keywords)}")
    else:
        st.write("**Matched (lemmatized + synonyms): None**")

    st.markdown("### Ranked by TF-IDF Importance")
    for word, score in ranked_keywords:
        st.write(f"- {word}: {score:.4f}")

    # ---- Generate resume with LLM ----
    with st.spinner("Calling LLM to generate updated resume..."):
        top_ranked_words = [word for word, _ in ranked_keywords[:10]]
        updated_json, raw_response = get_updated_resume_json(
            resume_core, job_desc, sections_to_update, PROTECTED_KEYS, top_ranked_words
        )

    st.markdown("### Debug: Collected LLM Raw Response")
    st.code(raw_response)

    # ---- Merge + save final resume ----
    final_resume = {**resume_core, **updated_json, **personal_info}

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
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            st.download_button("Download PDF", f, file_name=f"{safe_name}.pdf")
    if styled_docx_path and os.path.exists(styled_docx_path):
        with open(styled_docx_path, 'rb') as f:
            st.download_button("Download Styled DOCX", f, file_name=f"{safe_name}_styled.docx")

    st.markdown("---")
# ---- Footer ----
