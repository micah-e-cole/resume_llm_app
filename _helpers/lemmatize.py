# _helpers/lemmatize.py

import nltk
import os
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.data import find


def ensure_nltk_resources():
    """
    Ensure required NLTK resources are downloaded to the venv/nltk_data folder.
    """
    venv_base = os.path.dirname(os.path.dirname(nltk.__file__))
    nltk_data_dir = os.path.join(venv_base, 'nltk_data')

    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
        print(f"Created nltk_data directory at {nltk_data_dir}")

    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)

    resources = [
        'punkt',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng'  # ✅ NEW: required by nltk.pos_tag(lang="eng")
    ]

    for resource in resources:
        try:
            if resource == 'punkt':
                nltk.data.find(f'tokenizers/{resource}')
            elif 'tagger' in resource:
                nltk.data.find(f'taggers/{resource}')
            else:
                nltk.data.find(f'corpora/{resource}')
            print(f"NLTK resource '{resource}' already installed in venv.")
        except LookupError:
            print(f"Downloading NLTK resource '{resource}' to {nltk_data_dir}...")
            nltk.download(resource, download_dir=nltk_data_dir)
    print("All required NLTK resources are ready.")

def patched_pos_tag(tokens):
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')
    return nltk.pos_tag(tokens)


lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(tag):
    """
    Map NLTK POS tag to WordNet POS tag.
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatize_text(text):
    """
    Lemmatize the input text using WordNetLemmatizer and patched POS tagging.
    Returns a list of lemmas (base words).
    """
    tokens = word_tokenize(text.lower())
    pos_tags = patched_pos_tag(tokens)
    lemmas = [lemmatizer.lemmatize(token, get_wordnet_pos(pos)) for token, pos in pos_tags]
    return lemmas


def get_synonyms(word):
    """
    Get WordNet synonyms for a word.
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace('_', ' '))
    return synonyms


def compute_tfidf_scores(texts):
    """
    Compute TF-IDF scores for a list of documents.
    """
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    scores_list = []
    for row in X:
        scores = {feature_names[col]: row[0, col] for col in row.nonzero()[1]}
        scores_list.append(scores)
    return scores_list


def match_keywords_with_synonyms(job_desc, resume_text):
    """
    Match keywords between job description and resume using lemmatization and synonyms.
    """
    job_lems = set(lemmatize_text(job_desc))
    resume_lems = set(lemmatize_text(resume_text))
    expanded_job = job_lems.copy()
    for word in job_lems:
        expanded_job.update(get_synonyms(word))
    matched = expanded_job.intersection(resume_lems)
    return list(matched)


def rank_matched_keywords_by_tfidf(matched_keywords, texts):
    """
    Rank matched keywords by average TF-IDF score.
    """
    scores_list = compute_tfidf_scores(texts)
    combined_scores = {}
    for word in matched_keywords:
        score_job = scores_list[0].get(word, 0)
        score_resume = scores_list[1].get(word, 0)
        avg_score = (score_job + score_resume) / 2
        combined_scores[word] = avg_score
    sorted_ranked = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_ranked
