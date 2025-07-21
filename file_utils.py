# file_utils.py
import json
import os
import difflib
import pypandoc
from styler import apply_styles_to_docx

def load_json(filepath):
    with open(filepath) as f:
        return json.load(f)

def save_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def convert_to_pdf(md_path, folder, name):
    pdf_path = os.path.join(folder, f"{name}.pdf")
    try:
        pypandoc.convert_file(md_path, 'pdf', outputfile=pdf_path)
        return pdf_path
    except Exception as e:
        print(f"PDF conversion failed: {e}")
        return None

def convert_to_docx(md_path, folder, name):
    docx_path = os.path.join(folder, f"{name}.docx")
    try:
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
        return docx_path
    except Exception as e:
        print(f"DOCX conversion failed: {e}")
        return None

def apply_docx_styles(docx_path, style_json, folder, name):
    styled_path = os.path.join(folder, f"{name}_styled.docx")
    try:
        apply_styles_to_docx(docx_path, style_json, styled_path)
        return styled_path
    except Exception as e:
        print(f"Styling DOCX failed: {e}")
        return None

def generate_diff(old, new):
    diff = '\n'.join(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=''))
    return diff
