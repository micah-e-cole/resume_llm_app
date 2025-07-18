import streamlit as st
import json
import requests
import subprocess
import os
from jinja2 import Environment, FileSystemLoader
import pypandoc
import difflib

# ---- SETUP ----
# Ensure output folder exists
os.makedirs('output', exist_ok=True)

# ---- STREAMLIT APP ----
st.title("Resume Tailoring App with LLM + Pandoc")

st.markdown("Upload your resume JSON and paste a job description. This app will tailor your resume using a local LLM (Ollama) and generate updated PDF and DOCX files.")

# Input fields
organization = st.text_input("Organization Name (e.g., Google)")
job_title = st.text_input("Job Title (e.g., Software Engineer)")
job_desc = st.text_area("Paste Job Description", height=300)
resume_file = st.file_uploader("Upload Resume JSON", type=["json"])
sections_to_update = st.multiselect("Select sections to rewrite", ["summary", "skills", "experience"], default=["summary", "skills", "experience"])

if st.button("Generate Updated Resume"):
    if job_desc and resume_file and organization and job_title:
        # ---- LOAD RESUME ----
        resume_data = json.load(resume_file)
        first_name = resume_data.get('name', 'First Last').split()[0]
        last_name = resume_data.get('name', 'First Last').split()[-1]
        safe_org = organization.replace(' ', '_')
        safe_job = job_title.replace(' ', '_')
        safe_name = f"{first_name}_{last_name}_{safe_job}"
        org_folder = os.path.join('output', safe_org)
        os.makedirs(org_folder, exist_ok=True)

        # ---- BUILD PROMPT ----
        prompt = f"""
        You are a resume assistant.
        Here is my resume (in JSON): {resume_data}
        Here is the job description: {job_desc}
        Please suggest updates ONLY for these sections: {', '.join(sections_to_update)}.
        Return ONLY updated JSON.
        """

        # ---- CALL OLLAMA API ----
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={'model': 'llama3:8b', 'prompt': prompt},
                timeout=120  # increase if needed
            )
            response.raise_for_status()
            updated_json = json.loads(response.json()['response'])
        except Exception as e:
            st.error(f"LLM call failed: {e}")
            st.stop()

        # ---- SHOW DIFF (SUMMARY ONLY) ----
        old_summary = resume_data.get('summary', '')
        new_summary = updated_json.get('summary', '')
        diff_summary = difflib.ndiff(old_summary.splitlines(), new_summary.splitlines())
        st.markdown("### 🔍 Summary Diff")
        st.code('\n'.join(diff_summary))

        # ---- RENDER MARKDOWN USING JINJA2 ----
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('resume_template.md')
        rendered_md = template.render(updated_json)

        # ---- SAVE MARKDOWN ----
        md_path = os.path.join(org_folder, f"{safe_name}.md")
        with open(md_path, 'w') as f:
            f.write(rendered_md)

        # ---- CONVERT TO PDF AND DOCX USING PANDOC ----
        pdf_path = os.path.join(org_folder, f"{safe_name}.pdf")
        docx_path = os.path.join(org_folder, f"{safe_name}.docx")
        
        pypandoc.convert_file(md_path, 'pdf', outputfile=pdf_path)
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)

        # ---- SHOW DOWNLOAD BUTTONS ----
        st.success(f"Files saved to {org_folder}")
        with open(pdf_path, 'rb') as f:
            st.download_button("📥 Download PDF", f, file_name=f"{safe_name}.pdf")
        with open(docx_path, 'rb') as f:
            st.download_button("📥 Download DOCX", f, file_name=f"{safe_name}.docx")

        # ---- EXTRA NOTES ----
        st.markdown("---")
        st.markdown("**🔧 How to edit:**")
        st.markdown("- To change the LLM, modify `'model': 'llama3:8b'` in the code.")
        st.markdown("- To change prompt style, edit the `prompt` string.")
        st.markdown("- To adjust Markdown-to-PDF style, edit the `resume_template.md` file or pass a custom reference DOCX to Pandoc.")
    else:
        st.warning("Please fill in all fields and upload resume JSON.")
