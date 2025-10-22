import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

class SmallTalkHandler:
    def __init__(self, data_path="datasets/small_talk.csv"):
        self.data_path = data_path
        self.questions = []
        self.answers = []
        self.vectorizer = None
        self.questions_tfidf = None
        self.lemmatizer = WordNetLemmatizer()
        self._load_data()
        self._train_model()
        
    def _preprocess(self, text):
        text = text.lower()
        tokens = word_tokenize(text)
        lemmatized_tokens = []
        for word in tokens:
            if word.isalnum():
                 lemmatized_tokens.append(self.lemmatizer.lemmatize(word))
        return ' '.join(lemmatized_tokens)

    def _load_data(self):
        full_path = self.data_path 
        try:
            df = pd.read_csv(full_path)        
            if 'Question' not in df.columns or 'Answer' not in df.columns:
                 print("Error: Check CSV")
                 return  
            self.questions = [self._preprocess(q) for q in df['Question'].tolist()]
            self.answers = df['Answer'].tolist()
        except Exception as e:
            print(f"An error occurred loading small talk data: {e}")
            return

    def _train_model(self):
        if not self.questions:
            print("Warning: No small talk questions loaded")
            return   
        self.vectorizer = TfidfVectorizer()
        self.questions_tfidf = self.vectorizer.fit_transform(self.questions)

    def get_small_talk_response(self, query, threshold):
        if self.questions_tfidf is None or self.vectorizer is None:
            return "Sorry, the small talk module is not initialized correctly."
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
            return self.answers[best_match_index]
        else:
            return None