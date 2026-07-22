import re
import string
import nltk
import spacy

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt_tab')
nltk.download('stopwords')

nlp = spacy.load('en_core_web_sm')

stop_words = set(stopwords.words('english'))

class TextPreprocessor:

    def lowercase(self, text):
        return text.lower()

    def remove_emails(self, text):
        return re.sub(r'\S+@\S+', '', text)

    def remove_urls(self, text):
        return re.sub(r'http\S+www\S', '', text)

    def remove_phone_numbers(self, text):
        return re.sub(r'\+?\d[\d\s\-]{8,}\d', '', text)

    def remove_punctuation(self, text):
        return text.translate(
            str.maketrans('', '', string.punctuation)
        )

    def remove_numbers(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def tokenize(self, text):
        return word_tokenize(text)

    def remove_extra_spaces(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def remove_stopwords(self, tokens):

        return [
            word
            for word in tokens
            if word not in stop_words
        ]

    def lemmatize(self, tokens):

        sentence = " ".join(tokens)

        doc = nlp(sentence)

        return [
            token.lemma_
            for token in doc

        ]

    def preprocess(self, text):

        text = self.lowercase(text)

        text = self.remove_emails(text)

        text = self.remove_urls(text)

        text = self.remove_phone_numbers(text)

        text = self.remove_punctuation(text)

        text = self.remove_numbers(text)

        text = self.remove_extra_spaces(text)

        tokens = self.tokenize(text)

        tokens = self.remove_stopwords(tokens)

        tokens = self.lemmatize(tokens)

        return " ".join(tokens)