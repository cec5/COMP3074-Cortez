import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
#from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class IntentClassifier:
    def __init__(self, data_path="datasets/intents_data.csv"):
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        self.intent_phrases_tfidf = None
        self.phrases = []
        self.intents = []
        self._load_and_train(data_path)

    def _preprocess(self, text):
        text = text.lower()
        tokens = word_tokenize(text)
        lemmatized_tokens = []
        for word in tokens:
            if word.isalnum():
                 lemmatized_tokens.append(self.lemmatizer.lemmatize(word))
        return ' '.join(lemmatized_tokens)

    def _load_and_train(self, data_path):
        try:
            df = pd.read_csv(data_path)
            self.phrases = [self._preprocess(p) for p in df['Phrase'].tolist()]
            self.intents = df['Intent'].tolist()
            self.vectorizer = TfidfVectorizer(analyzer='word')
            self.intent_phrases_tfidf = self.vectorizer.fit_transform(self.phrases)
        except Exception as e:
            print(f"[SYSTEM ERROR]: Error with loading or training intent data: {e}")
            self.vectorizer = None

    def classify(self, query, threshold):
        if self.vectorizer is None:
            return "SystemError", 0.0
        processed_query = self._preprocess(query)
        if not processed_query.strip():
            return "SystemError", 0.0
        query_tfidf = self.vectorizer.transform([processed_query])
        if query_tfidf.sum() == 0:
            return "Unrecognized", 0.0
        similarity_scores = cosine_similarity(query_tfidf, self.intent_phrases_tfidf)[0]
        best_match_index = np.argmax(similarity_scores)
        best_score = similarity_scores[best_match_index]
        if best_score >= threshold:
            return self.intents[best_match_index], best_score
        else:
            return "Unrecognized", best_score