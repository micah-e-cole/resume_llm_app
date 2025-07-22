# _helpers/lemmatize.py

import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Helper: map NLTK POS tags to WordNet POS tags
def get_wordnet_pos(tag):
    """
    Convert NLTK POS tags to WordNet POS tags for more accurate lemmatization.
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
        return wordnet.NOUN  # default fallback

# Lemmatize a single text string into a list of base words
def lemmatize_text(text):
    """
    Lemmatize the input text using WordNetLemmatizer and POS tagging.
    Returns a list of lemmas (base words).
    """
    tokens = word_tokenize(text.lower())
    pos_tags = nltk.pos_tag(tokens)
    lemmas = [lemmatizer.lemmatize(token, get_wordnet_pos(pos)) for token, pos in pos_tags]
    return lemmas

# Get synonyms for a given word using WordNet
def get_synonyms(word):
    """
    Return a set of synonyms for a word from WordNet.
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace('_', ' '))
    return synonyms

# Compute TF-IDF scores for each document in a list of texts
def compute_tfidf_scores(texts):
    """
    Input: texts (list of strings)
    Output: list of dictionaries with {word: tfidf_score}
    """
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    scores_list = []
    for row in X:
        scores = {feature_names[col]: row[0, col] for col in row.nonzero()[1]}
        scores_list.append(scores)
    return scores_list

# Match keywords between job description and resume using lemmatization + synonyms
def match_keywords_with_synonyms(job_desc, resume_text):
    """
    Match keywords between job description and resume text.
    Uses lemmatization and synonyms to find overlapping words.
    Returns a list of matched keywords.
    """
    job_lems = set(lemmatize_text(job_desc))
    resume_lems = set(lemmatize_text(resume_text))

    # Expand job description lemmas with synonyms
    expanded_job = job_lems.copy()
    for word in job_lems:
        expanded_job.update(get_synonyms(word))

    # Find overlap between expanded job lemmas and resume lemmas
    matched = expanded_job.intersection(resume_lems)
    return list(matched)

# Rank matched keywords by average TF-IDF score across both texts
def rank_matched_keywords_by_tfidf(matched_keywords, texts):
    """
    Input:
        matched_keywords: list of matched words
        texts: [job_desc, resume_text]
    Output:
        sorted list of (word, avg_tfidf_score)
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