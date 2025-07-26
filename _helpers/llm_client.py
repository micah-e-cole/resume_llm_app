# llm_client.py

# import necessary libraries
import requests
import json
import re
import shutil
from .constants import STOPWORDS, MODEL_NAME, PROTECTED_KEYS

def separate_protected_sections(data):
    '''
    Separate protected sections from the main resume data.
    Returns a tuple of (non-protected, protected) dictionaries.
    Protected sections are defined by PROTECTED_KEYS.
    '''
    protected = {k: data.get(k, []) for k in PROTECTED_KEYS}
    non_protected = {k: v for k, v in data.items() if k not in PROTECTED_KEYS}
    return non_protected, protected

def clean_json_like_text(text):
    '''
    Clean LLM output to be valid JSON.
    - Remove code block markers
    - Convert single quotes to double quotes for keys
    - Ensure string values are properly quoted
    '''
    text = re.sub(r'```json|```', '', text).strip()
    text = re.sub(r"'(\w+)':", r'"\1":', text)
    text = re.sub(r':\s*\'([^\']*)\'', r': "\1"', text)
    return text

def extract_json_from_text(text):
    """
    Extract and clean first JSON block from LLM response.
    Handles minor format issues like trailing commas.
    """
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON object found in response.")

    json_block = match.group(0)
    cleaned_json = clean_json_like_text(json_block)

    # Fix trailing commas before closing } or ]
    cleaned_json = re.sub(r',(\s*[}\]])', r'\1', cleaned_json)

    # Optional: Ensure lists are properly closed (quick patch for common LLM cutoffs)
    open_brackets = cleaned_json.count('[')
    close_brackets = cleaned_json.count(']')
    if close_brackets < open_brackets:
        cleaned_json += ']' * (open_brackets - close_brackets)

    open_braces = cleaned_json.count('{')
    close_braces = cleaned_json.count('}')
    if close_braces < open_braces:
        cleaned_json += '}' * (open_braces - close_braces)

    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decoding failed after cleaning: {e}\nCleaned JSON: {cleaned_json}")


def extract_keywords(text, top_n=15):
    '''
    Extract top keywords from text using simple frequency-based method.
    Filters out common stopwords defined in constants.py.
    Returns a list of top N keywords.
    '''
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    freq = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_keywords[:top_n]]

def get_updated_resume_json(resume_core, job_desc, sections, ranked_keywords, skills_max_count=8):
    '''
    Call the LLM to generate an updated resume JSON based on the core resume,
    job description, and sections to update. Ranked keywords are included to guide the LLM.
    Returns the updated JSON and the raw LLM response text.
    '''
    llm_input, _ = separate_protected_sections(resume_core)

    # Incorporate the TF-IDF keywords into the prompt
    keywords_str = ', '.join([kw for kw, _ in ranked_keywords]) if ranked_keywords else ""

    prompt = (
        "You are an expert resume assistant specialized in ATS-optimized resumes.\n"
        f"Resume data: {json.dumps(llm_input)}\n"
        f"Job description: {job_desc}\n"
        f"Update sections: {', '.join(sections)}.\n"
        f"Focus on incorporating or improving emphasis on the following important skills and keywords: {keywords_str}.\n"
        f"Only include up to {skills_max_count} skills in the 'skills' section.\n"
        "Return ONLY a valid JSON object, no markdown, no comments, no explanations."
    )

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': MODEL_NAME, 'prompt': prompt},
        stream=True,
        timeout=180
    )

    collected = []
    for line in response.iter_lines():
        if line:
            decoded = json.loads(line.decode('utf-8') if isinstance(line, bytes) else line)
            chunk = decoded.get("response", "")
            collected.append(chunk)
    full_text = ''.join(collected)
    updated_json = extract_json_from_text(full_text)

    # Post-process to enforce max skills
    if "skills" in updated_json and isinstance(updated_json["skills"], list):
        updated_json["skills"] = updated_json["skills"][:skills_max_count]

    return updated_json, full_text

def check_pandoc_engine():
    '''
    Check if Pandoc is installed and can convert files.
    Returns True if Pandoc is available, False otherwise.
    '''
    return bool(shutil.which('pdflatex'))
