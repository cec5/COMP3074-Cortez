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
        self.intent_phrases_tfidf = None
        self.phrases = []
        self.intents = []
        self.stopwords = set(stopwords.words('english'))
        self.name_ignore = ["call","name","my","to","please","yes","is","i","am","know","who","tell","change","want","wish","rename","switch","update","remember"]
        self._load_and_train(data_path)

    def _preprocess(self, text):
        text = text.lower()
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) for word in tokens if word.isalnum()]
        return ' '.join(lemmatized_tokens)

    def _load_and_train(self, data_path):
        try:
            df = pd.read_csv(data_path)
            self.phrases = [self._preprocess(p) for p in df['Phrase'].tolist()]
            self.intents = df['Intent'].tolist()
            self.vectorizer = TfidfVectorizer(analyzer='word')
            self.intent_phrases_tfidf = self.vectorizer.fit_transform(self.phrases)
        except Exception as e:
            print(f"SYSTEM: Error loading identity dataset: {e}")
            self.vectorizer = None

    def _classify(self, query, threshold):
        if self.vectorizer is None:
            return "SystemError", 0.0
        processed_query = self._preprocess(query)
        if not processed_query.strip():
            return "EmptyQuery", 0.0
        query_tfidf = self.vectorizer.transform([processed_query])
        if query_tfidf.sum() == 0:
            return "Unrecognized", 0.0
        similarity_scores = cosine_similarity(query_tfidf, self.intent_phrases_tfidf)[0]
        best_index = np.argmax(similarity_scores)
        best_score = similarity_scores[best_index]
        if best_score >= threshold:
            return self.intents[best_index], best_score
        else:
            return "Unrecognized", best_score

    def _extract_possible_name(self, query):
        tokens = word_tokenize(query.lower())
        filtered = [t for t in tokens if t.isalpha() and t not in self.name_ignore and t not in self.stopwords]
        if not filtered:
            return None
        return filtered[-1].capitalize()
    
    def _name_loop(self, username, stop=False):
        print("JOSEFINA: Very well! Type in your name below!")
        while not stop:
            new_name = input().strip()
            if new_name:
                if new_name == "CANCEL":
                    return ("JOSEFINA: I've cancelled the current action, what now?", username)
                else:
                    return (f"JOSEFINA: Got it, you are {new_name}!", new_name)
            else:
                print("JOSEFINA: I didn't quite get that, please type your name below!")

    def _ask_user_for_name(self, username, stop=False, i=0):
        print("JOSEFINA: I don't think you've told me your name yet, would you like to set it?")
        while not stop and i < 2:
            response = input("USER: ").strip()
            if response == "CANCEL":
                return ("JOSEFINA: I've cancelled the current action, what now?", username)
            elif any(word in response.lower() for word in ["yes","ok","alright"]):
                return self._name_loop(username)
            elif "no" in response.lower():
                return ("JOSEFINA: Alright then!", username)
            else:
                i += 1
                if i < 2: print("JOSEFINA: I couldn't understand your reply, can you try again?")
        else:
            return ("JOSEFINA: I still can't understand your reply, let's move on.", username)

    def get_identity_response(self, query, username, threshold=0.3):
        query = query.strip()
        intent, score = self._classify(query, threshold)

        if intent == "Identification":
            if username:
                return (f"JOSEFINA: You are {username}.", username)
            else:
                return self._ask_user_for_name(username)
        elif intent == "NameDirect":
            new_name = self._extract_possible_name(query)
            if new_name:
                return (f"JOSEFINA: Nice to meet you, {new_name}. I’ll remember you.", new_name)
            else:
                return ("JOSEFINA: I couldn't quite catch your name there.", username)
        elif intent == "NameChange":
            return self._name_loop(username)
        elif intent == "NameDelete":
            if username:
                return (f"JOSEFINA: I’ve forgotten your name, {username}.", None)
            else:
                return ("JOSEFINA: I don’t think I know your name yet.", username)
        elif intent == "Unrecognized":
            return ("JOSEFINA: I’m not sure what you mean about your name.", username)
        elif intent == "SystemError":
            return ("SYSTEM: Error in identity processing.", username)
        else:
            return ("JOSEFINA: I’m not sure how to handle that request about your name.", username)