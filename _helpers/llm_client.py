# llm_client.py

# import necessary libraries
import requests
import json
import re
from .constants import STOPWORDS, MODEL_NAME, PROTECTED_KEYS

def separate_protected_sections(data):
    '''
    Separate protected sections from the main resume data.
    Returns a tuple of (non-protected, protected) dictionaries.
    Protected sections are defined by PROTECTED_KEYS.
    '''

    protected = {k: data.get(k, []) for k in PROTECTED_KEYS}
    # Create a new dictionary excluding the protected keys
    # This allows the LLM to focus on the sections that need updating
    # while preserving important information.
    # The non-protected sections will be passed to the LLM for processing.
    # The protected sections will be merged back into the final resume after LLM processing.
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
    # Convert single quotes to double quotes for keys and values
    text = re.sub(r"'(\w+)':", r'"\1":', text)
    # Ensure string values are properly quoted
    text = re.sub(r':\s*\'([^\']*)\'', r': "\1"', text)
    # Remove any trailing commas
    return text

def extract_json_from_text(text):
    """
    Extract and clean first JSON block from LLM response.
    """
    # Match first {...} block only
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        # Extract the matched JSON block
        json_block = match.group(0)
        # Clean the JSON block to ensure it is valid
        cleaned_json = clean_json_like_text(json_block)
        try:
            # Attempt to parse the cleaned JSON
            # This will raise an error if the JSON is still invalid
            return json.loads(cleaned_json)
        # Catch JSON decoding errors and provide context
        # This helps identify issues in the LLM response
        except json.JSONDecodeError as e:
            # If JSON decoding fails, print the error and cleaned JSON
            raise ValueError(f"JSON decoding failed after cleaning: {e}\nCleaned JSON: {cleaned_json}")
    # If no valid JSON block is found, raise an error
    raise ValueError("No valid JSON object found in response.")

def extract_keywords(text, top_n=15):
    '''
    Extract top keywords from text using simple frequency-based method.
    Filters out common stopwords defined in constants.py.
    Returns a list of top N keywords.
    '''
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out stopwords and short words
    # This helps focus on meaningful keywords and avoids noise from common words.
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    # Count frequency of each keyword
    # This allows identifying the most relevant keywords based on their occurrence in the text.
    # The frequency count is used to determine the top N keywords.
    freq = {}
    for word in filtered:
        # Increment the count for each word
        # This builds a frequency dictionary where each word maps to its count.
        freq[word] = freq.get(word, 0) + 1
        # Sort keywords by frequency and return the top N
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    # Return only the top N keywords
    return [kw for kw, _ in sorted_keywords[:top_n]]

def get_updated_resume_json(resume_core, job_desc, sections, protected_keys):
    '''
    Call the LLM to generate an updated resume JSON based on the core resume,
    job description, and sections to update.
    Returns the updated JSON and the raw LLM response text.
    '''
    llm_input, _ = separate_protected_sections(resume_core)
    # Prepare the prompt for the LLM
    # This includes the core resume data, job description, and sections to update.
    # Prompt message sent to the model
    prompt = (
        "You are an expert resume assistant specialized in ATS-optimized resumes.\n"
        f"Resume data: {json.dumps(llm_input)}\n"
        f"Job description: {job_desc}\n"
        f"Update sections: {', '.join(sections)}.\n"
        "Return ONLY a valid JSON object, no markdown, no comments, no explanations."
    )

    # Call the LLM API
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': MODEL_NAME, 'prompt': prompt},
        stream=True,
        timeout=180
    )

    collected = []
    # Collect the response text
    # Iterate over the response stream
    # This allows handling large responses without loading everything into memory at once
    for line in response.iter_lines():
        # Decode bytes to string if necessary
        if line:
            collected.append(line.decode('utf-8') if isinstance(line, bytes) else line)
    # Join all collected lines into a single string
    full_text = ''.join(collected)
    # Extract the JSON from the full text
    return extract_json_from_text(full_text), full_text

def check_pandoc_engine():
    '''
    Check if Pandoc is installed and can convert files.
    Returns True if Pandoc is available, False otherwise.
    '''
    import shutil
    # Check if Pandoc is in the system PATH
    # This is a simple check to see if the command 'pandoc' can be found
    # It does not check if Pandoc is fully functional, just its presence.
    return bool(shutil.which('pdflatex'))
