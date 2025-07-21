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

Files included:
- main.py: Streamlit app logic
- llm_client.py: LLM interaction and JSON handling
- constants.py: Application constants
- styler.py: DOCX styling functions
- file_utils.py: File handling utilities
'''
# import necessary libraries
import streamlit as st
import json
import os
from llm_client import get_updated_resume_json, extract_keywords, check_pandoc_engine
from file_utils import load_json, save_file, convert_to_pdf, convert_to_docx, apply_docx_styles, generate_diff
from constants import PROTECTED_KEYS

# ---- Setup ----
# Ensure necessary directories exist
os.makedirs('resumes', exist_ok=True)
# Ensure output directory exists for generated files
os.makedirs('output', exist_ok=True)

# ---- Streamlit App Configuration ----
# Set up the Streamlit page configuration
# This includes the title and layout of the app.
st.set_page_config(page_title="Resume Tailoring App", layout="wide")
st.title("Resume Tailoring App")
# Display a brief description of the app
st.markdown("""
Paste a job description, select sections to update, and generate a tailored resume.

**Personal details and fixed sections are protected from LLM exposure.**
""")

# ---- Input Fields ----
# Input fields for user to enter job description and select sections to update
focus_area = st.selectbox("Select Resume Focus Area", ["IT", "Software Development", "Security"])
organization = st.text_input("Organization Name", value="")
job_title = st.text_input("Job Title", value="")
job_desc = st.text_area("Paste Job Description", height=300, value="")
# Select sections to update in the resume
# This allows the user to choose which parts of the resume they want to modify.
sections_to_update = st.multiselect(
    "Select sections to rewrite",
    ["summary", "skills", "experience", "projects", "technical-tools", "strengths"],
    default=["summary", "skills", "experience", "projects", "technical-tools", "strengths"]
)

# ---- Generate Updated Resume ----
# Button to trigger the resume generation process
if st.button("Generate Updated Resume"):
    # Validate inputs
    # Ensure all required fields are filled before proceeding
    if not (job_desc and organization and job_title):
        # Display an error message if inputs are missing
        st.warning("Please fill in all fields.")
        # Stop further execution if validation fails
        st.stop()

    # Load core resume and personal info
    with st.spinner("Loading resume and personal info..."):
        # Load the core resume JSON based on the selected focus area
        resume_file = f"resumes/{focus_area.lower().replace(' ', '_')}_resume.json"
        # Load personal information from a fixed JSON file
        personal_file = "personal_info.json"
        # Load the core resume and personal info JSON files
        resume_core = load_json(resume_file)
        # Load personal information from a fixed JSON file
        personal_info = load_json(personal_file)

    # Display the loaded resume core and personal info for debugging
    with st.spinner("Calling LLM to generate updated resume..."):
        # Call the LLM to get the updated resume JSON
        updated_json, raw_response = get_updated_resume_json(
            resume_core, job_desc, sections_to_update, PROTECTED_KEYS
        )

    # Display raw LLM response for debugging
    st.markdown("### Debug: Collected LLM Raw Response")
    st.code(raw_response)

    # Display the updated JSON for debugging
    with st.spinner("Extracting and matching job description keywords..."):
        # Extract keywords from the job description
        job_keywords = extract_keywords(job_desc, top_n=15)
        # Display the extracted keywords for debugging
        resume_text = json.dumps(updated_json).lower()
        # Check which keywords from the job description are present in the updated resume
        matched_keywords = [kw for kw in job_keywords if kw in resume_text]

    # Display the matched keywords for debugging
    st.markdown("### Keyword Match Check")
    # Display the job description keywords and matched keywords
    st.write(f"**Top job description keywords:** {', '.join(job_keywords)}")
    # Display the matched keywords in the updated resume
    st.write(f"**Matched in updated resume:** {', '.join(matched_keywords) or 'None'}")

    # Merge sections
    final_resume = {**resume_core, **updated_json, **personal_info}

    # Create safe filenames
    # Extract first and last names from personal info
    first_name = personal_info.get('name', 'First Last').split()[0]
    last_name = personal_info.get('name', 'First Last').split()[-1]
    # Create a safe name for the output files
    # Replace spaces with underscores and remove special characters
    safe_org = organization.replace(' ', '_')
    safe_job = job_title.replace(' ', '_')
    safe_focus = focus_area.replace(' ', '')
    safe_name = f"{first_name}_{last_name}_{safe_focus}_{safe_job}"
    # Create output folder for the organization
    org_folder = os.path.join('output', safe_org)
    # Ensure the organization folder exists
    os.makedirs(org_folder, exist_ok=True)

    # Save the final resume as JSON
    with st.spinner("Generating diff summary..."):
        # Save the final resume JSON to a file
        diff_summary = generate_diff(resume_core.get('summary', ''), updated_json.get('summary', ''))
    st.markdown("### Summary Diff")
    st.code(diff_summary or "No changes.")

    with st.spinner("Rendering resume as Markdown..."):
        # Render the final resume as Markdown using Jinja2 template
        # Spinner to indicate rendering process
        from jinja2 import Environment, FileSystemLoader
        # Load the Jinja2 template for rendering the resume
        env = Environment(loader=FileSystemLoader('.'))
        # Load the resume template
        template = env.get_template('resume_template.md')
        # Render the template with the final resume data
        # This converts the final resume JSON into a Markdown format for display and saving. 
        rendered_md = template.render(final_resume)
        # Save the rendered Markdown to a file
        md_path = os.path.join(org_folder, f"{safe_name}.md")
        save_file(md_path, rendered_md)


    pdf_path, docx_path, styled_docx_path = None, None, None
    # Convert Markdown to PDF and DOCX

    with st.spinner("Converting to PDF and DOCX..."):
        # Convert the Markdown file to PDF and DOCX formats
        if check_pandoc_engine():
            # This uses the Pandoc tool to convert the Markdown file into PDF and DOCX formats
            pdf_path = convert_to_pdf(md_path, org_folder, safe_name)
            # Convert to DOCX format
        docx_path = convert_to_docx(md_path, org_folder, safe_name)

    with st.spinner("Applying styles to DOCX..."):
        # Apply styles to the DOCX file based on a JSON configuration
        # This uses the styler module to apply custom styles defined in a JSON file
        # The styles are applied to the DOCX file to enhance its appearance.
        styled_docx_path = apply_docx_styles(docx_path, 'styles.json', org_folder, safe_name)

    # Display success message and shows where files are saved
    st.success(f"Files saved to `{org_folder}`")

    # Download buttons
    if pdf_path and os.path.exists(pdf_path):
        # Display download buttons for the generated files
        with open(pdf_path, 'rb') as f:
            # Download the PDF file
            st.download_button("Download PDF", f, file_name=f"{safe_name}.pdf")
    if styled_docx_path and os.path.exists(styled_docx_path):
        # Download the styled DOCX file
        with open(styled_docx_path, 'rb') as f:
            # Download the styled DOCX file
            st.download_button("Download Styled DOCX", f, file_name=f"{safe_name}_styled.docx")

    st.markdown("---")
    # Display tips for using the app
    st.markdown("**Tip:** Adjust model or template format in `resume_template.md` as needed.")
# ---- End of main.py ----
