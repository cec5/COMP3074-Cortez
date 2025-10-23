import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
#from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class SmallTalkHandler:
    def __init__(self, data_path="datasets/small_talk.csv"):
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        self.questions_tfidf = None
        self.questions = []
        self.answers = []
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
            self.answers = df['Answer'].tolist()
            self.vectorizer = TfidfVectorizer(analyzer='word')
            self.questions_tfidf = self.vectorizer.fit_transform(self.questions)
        except Exception as e:
            print(f"SYSTEM: Error loading small talk data: {e}")
            self.vectorizer = None

    def get_small_talk_response(self, query, threshold):
        if self.questions_tfidf is None or self.vectorizer is None:
            return None
        processed_query = self._preprocess(query)
        if not processed_query.strip():
            return None
        query_tfidf = self.vectorizer.transform([processed_query])
        if query_tfidf.sum() == 0:
            return None  
        similarity_scores = cosine_similarity(query_tfidf, self.questions_tfidf)[0]
        best_match_index = np.argmax(similarity_scores)
        best_score = similarity_scores[best_match_index]
        if best_score >= threshold:
            return f"JOSEFINA: {self.answers[best_match_index]}"
        else:
            return None
