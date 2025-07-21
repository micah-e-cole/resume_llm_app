# constants.py
'''
Constants and configurations for the resume LLM application.

PROTECTED_KEYS: List of keys in the resume JSON that should not be modified by the LLM.
MODEL_NAME: The name of the LLM model to use for generating resume updates.
STOPWORDS: Set of common words to filter out during keyword extraction.
'''
# ---- Constants/Keywords ----
# These sections of the resume are protected and should not be modified by the LLM.
# They will be merged back into the final resume after LLM processing.
# This allows the LLM to focus on the sections that need updating while preserving important information.
# Add any additional keys that should be protected from LLM modification.
PROTECTED_KEYS = ["education", "certificates"]

# Current model name used for LLM requests
# This can be changed based on the available models or user preference.
# Ensure this matches the model names available in your LLM service.
# Example: "llama3:8b" for Llama 3 8B
MODEL_NAME = "llama3:8b"  # Default model for LLM requests

# List of common stopwords to filter out from keyword extraction
# This can be expanded based on specific needs
# or language requirements.
STOPWORDS = set([
    'the', 'and', 'for', 'with', 'you', 'are', 'this', 'that', 'from', 'they',
    'their', 'your', 'will', 'have', 'has', 'but', 'not', 'all', 'any', 'can',
    'may', 'such', 'a', 'an', 'of', 'in', 'on', 'at', 'by', 'to', 'is', 'it',
    'be', 'as', 'or', 'if'
])
# Add more stopwords as needed