import unittest
import _helpers.lemmatize as lemmatize

class TestLemmatizeHelpers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        lemmatize.ensure_nltk_resources()  # Ensure NLTK resources are available before tests

    def test_lemmatize_text(self):
        text = "Cats are running quickly"
        result = lemmatize.lemmatize_text(text)
        self.assertIn("cat", result)
        self.assertIn("run", result)

    def test_get_synonyms(self):
        synonyms = lemmatize.get_synonyms("quick")
        self.assertIn("fast", synonyms)

    def test_match_keywords_with_synonyms(self):
        jd = "Looking for someone who can develop software and work with data"
        resume = "I have experience in software engineering and data analytics"
        matched = lemmatize.match_keywords_with_synonyms(jd, resume)
        self.assertIn("software", matched)
        self.assertIn("data", matched)
