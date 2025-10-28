import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class IdentityManagement:
    def __init__(self, data_path="datasets/identity.csv"):
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        self.questions_tfidf = None
        self.questions = []
        self.stopwords = set(stopwords.words('english'))
        self.name_ignore = ["call","name","my","to","please","yes","is","i","am","know","who","tell","change","want","wish","rename","switch","update"]
        self.name_change = ["change","rename","switch","update","remove","forget","delete"]
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
            self.questions = [self._preprocess(q) for q in df['Question'].tolist()]
            self.vectorizer = TfidfVectorizer(analyzer='word')
            self.questions_tfidf = self.vectorizer.fit_transform(self.questions)
        except Exception as e:
            print(f"SYSTEM: Error loading identity dataset: {e}")
            self.vectorizer = None

    def _extract_possible_name(self, query):
        tokens = word_tokenize(query.lower())
        filtered = [t for t in tokens if t.isalpha() and t not in self.name_ignore and t not in self.stopwords]
        if not filtered:
            return None
        return filtered[-1].capitalize()

    def get_identity_response(self, query, username, threshold=0.2):
        if self.vectorizer is None:
            return ("SYSTEM: Error with identity processing", username)

        processed_query = self._preprocess(query)
        if not processed_query.strip():
            return ("JOSEFINA: Could you say that again?", username)

        query_tfidf = self.vectorizer.transform([processed_query])
        similarity_scores = cosine_similarity(query_tfidf, self.questions_tfidf)[0]
        best_score = np.max(similarity_scores)

        if any(word in processed_query for word in self.name_change):
            if "forget" in processed_query or "remove" in processed_query or "delete" in processed_query:
                if username:
                    return (f"JOSEFINA: I've forgotten your name, {username}.", None)
                else:
                    return ("JOSEFINA: I don't think I know your name yet.", username)
            else:
                new_name = self._extract_possible_name(query)
                if new_name:
                    return (f"JOSEFINA: Sure, I'll now remember you as {new_name}.", new_name)
                else:
                    return ("JOSEFINA: What would you like me to call you instead?", username)

        if any(word in processed_query for word in ["name", "call", "am"]):
            new_name = self._extract_possible_name(query)
            if new_name:
                return (f"JOSEFINA: Got it! I'll remember you as {new_name}.", new_name)
    
        if best_score >= threshold:
            if username:
                return (f"JOSEFINA: You are {username}.", username)
            else:
                return ("JOSEFINA: I don't think you've told me your name yet.", username)
        return ("JOSEFINA: I'm not sure I understood that about your name.", username)