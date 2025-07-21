# llm_client.py
import requests
import json
import re
from constants import STOPWORDS, MODEL_NAME, PROTECTED_KEYS

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
    """
    # Match first {...} block only
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        json_block = match.group(0)
        cleaned_json = clean_json_like_text(json_block)
        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decoding failed after cleaning: {e}\nCleaned JSON: {cleaned_json}")
    raise ValueError("No valid JSON object found in response.")

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

def get_updated_resume_json(resume_core, job_desc, sections, protected_keys):
    '''
    Call the LLM to generate an updated resume JSON based on the core resume,
    job description, and sections to update.
    Returns the updated JSON and the raw LLM response text.
    '''
    llm_input, _ = separate_protected_sections(resume_core, protected_keys)
    prompt = (
        "You are an expert resume assistant specialized in ATS-optimized resumes.\n"
        f"Resume data: {json.dumps(llm_input)}\n"
        f"Job description: {job_desc}\n"
        f"Update sections: {', '.join(sections)}.\n"
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
            collected.append(line.decode('utf-8') if isinstance(line, bytes) else line)
    full_text = ''.join(collected)
    return extract_json_from_text(full_text), full_text

def check_pandoc_engine():
    '''
    Check if Pandoc is installed and can convert files.
    Returns True if Pandoc is available, False otherwise.
    '''
    import shutil
    return bool(shutil.which('pdflatex'))
