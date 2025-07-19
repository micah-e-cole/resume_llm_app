# render_resume.py
'''
Author: Micah Braun
Date: 2024-07-16
Version: 1.0

Description: This script is a Streamlit app that allows users to tailor their resumes based on job descriptions while protecting personal information and fixed sections. It uses a local LLM server to generate updates and outputs the final resume in PDF and DOCX formats. It also includes functionality to compare changes in the summary section.
'''
# imported libraries: streamlit, json, requests, os, jinja2, pypandoc, difflib
import streamlit as st
import json
import requests
import os
from jinja2 import Environment, FileSystemLoader
import pypandoc
import difflib

# ---- Helper function to extract and merge protected sections ----
''' 
Function Description: This function separates protected sections from the main resume data.

It returns two dictionaries: one for non-protected sections and another for protected sections.

Args:
    data (dict): The main resume data.
    protected_keys (list): List of keys that are considered protected.
Returns:
    tuple: A tuple containing two dictionaries - non-protected sections and protected sections.
'''
def separate_protected_sections(data, protected_keys):
    protected = {k: data.get(k, []) for k in protected_keys}
    non_protected = {k: v for k, v in data.items() if k not in protected_keys}
    return non_protected, protected

# ---- SETUP ----

# Ensure the required directories (resumes and output) exist
os.makedirs('resumes', exist_ok=True)
os.makedirs('output', exist_ok=True)

# ---- Streamlit app setup ----
st.set_page_config(page_title="Resume Tailoring App", layout="wide")
st.title("Resume Tailoring App with Focus Areas and Privacy")
# ---- Introduction ----
st.markdown("Select a focus area, paste a job description, and generate a tailored resume **without exposing personal details or fixed sections (like education and certificates) to the LLM**.")

# ---- Input fields ----
# Select focus area, organization, job title, and job description
st.markdown("### Input Details")
focus_area = st.selectbox("Select Resume Focus Area", ["IT", "Software Development", "Security"])
organization = st.text_input("Organization Name (e.g., Google, IBM, etc.)" , value="Enter Organization Name Here")
job_title = st.text_input("Job Title (e.g., Software Engineer, IT Specialist, etc.)", value="Enter Job Title Here")
job_desc = st.text_area("Paste Job Description", height=300, value="Paste job description here...")
sections_to_update = st.multiselect("Select sections to rewrite", ["summary", "skills", "experience", "projects", "technical-tools", "strengths"], default=["summary", "skills", "experience", "projects", "technical-tools", "strengths"])

if st.button("Generate Updated Resume"):
    if job_desc and organization and job_title:
        # resume_file_path = f"resumes/{focus_area.lower().replace(' ', '_')}_resume.json"
        if focus_area == "IT":
            resume_file_path = "resumes/it_resume.json"
        elif focus_area == "Software Development":
            resume_file_path = "resumes/software_development_resume.json"
        elif focus_area == "Security":
            resume_file_path = "resumes/security_resume.json"
        else:
            st.error("Unknown focus area selected.")
        st.stop()

        st.info(f"Loaded resume template for {focus_area}")

        try:
            with open(resume_file_path) as f:
                resume_core = json.load(f)
        except FileNotFoundError:
            st.error(f"Base resume file not found: {resume_file_path}")
            st.stop()

        try:
            with open('personal_info.json') as f:
                personal_info = json.load(f)
        except FileNotFoundError:
            st.error("personal_info.json not found. Please add your personal details file.")
            st.stop()

        # ---- Use helper to split protected sections ----
        protected_keys = ["education", "certificates"]
        llm_input, protected_sections = separate_protected_sections(resume_core, protected_keys)

        prompt = f"""
        You are a resume assistant.
        Here is my resume core data (excluding personal info and fixed sections): {llm_input}
        Here is the job description: {job_desc}
        Please suggest updates ONLY for these sections: {', '.join(sections_to_update)}.
        Return ONLY updated JSON.
        """

        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={'model': 'llama3:8b', 'prompt': prompt},
                timeout=120
            )
            response.raise_for_status()
            updated_json = json.loads(response.json()['response'])
        except Exception as e:
            st.error(f"LLM call failed: {e}")
            st.stop()

        # ---- Merge protected sections + personal info back ----
        final_resume = {**updated_json, **protected_sections, **personal_info}

        first_name = personal_info.get('name', 'First Last').split()[0]
        last_name = personal_info.get('name', 'First Last').split()[-1]
        safe_org = organization.replace(' ', '_')
        safe_job = job_title.replace(' ', '_')
        safe_focus = focus_area.replace(' ', '')
        safe_name = f"{first_name}_{last_name}_{safe_focus}_{safe_job}"
        org_folder = os.path.join('output', safe_org)
        os.makedirs(org_folder, exist_ok=True)

        old_summary = resume_core.get('summary', '')
        new_summary = updated_json.get('summary', '')
        diff_summary = difflib.ndiff(old_summary.splitlines(), new_summary.splitlines())
        st.markdown("### Summary Diff")
        st.code('\n'.join(diff_summary))

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('resume_template.md')
        rendered_md = template.render(final_resume)

        md_path = os.path.join(org_folder, f"{safe_name}.md")
        with open(md_path, 'w') as f:
            f.write(rendered_md)

        pdf_path = os.path.join(org_folder, f"{safe_name}.pdf")
        docx_path = os.path.join(org_folder, f"{safe_name}.docx")

        pypandoc.convert_file(md_path, 'pdf', outputfile=pdf_path)
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)

        st.success(f"Files saved to {org_folder}")
        with open(pdf_path, 'rb') as f:
            st.download_button("Download PDF", f, file_name=f"{safe_name}.pdf")
        with open(docx_path, 'rb') as f:
            st.download_button("Download DOCX", f, file_name=f"{safe_name}.docx")

        st.markdown("---")
        st.markdown("**How to edit:**")
        st.markdown("- Change the LLM model by modifying `'model': 'llama3:8b'`.")
        st.markdown("- Adjust the prompt wording in the `prompt` string.")
        st.markdown("- Edit `resume_template.md` to change the resume layout.")
    else:
        st.warning("Please fill in all fields.")
