import pandas as pd
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

pos_map = {'ADJ': 'a', 'ADV': 'r', 'NOUN': 'n', 'VERB': 'v'}

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
        tokens = nltk.word_tokenize(text.lower())
        tagged = nltk.pos_tag(tokens, tagset='universal')
        return ' '.join(self.lemmatizer.lemmatize(w, pos=pos_map.get(t, 'n')) for w, t in tagged if w.isalnum())

    def _load_and_train(self, data_path):
        try:
            df = pd.read_csv(data_path)
            self.phrases = [self._preprocess(p) for p in df['Phrase'].tolist()]
            self.intents = df['Intent'].tolist()
            self.vectorizer = TfidfVectorizer(analyzer='word')
            self.intent_phrases_tfidf = self.vectorizer.fit_transform(self.phrases)
        except Exception as e:
            print(f"[SYSTEM ERROR]: Error loading identity dataset: {e}")
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
    
    def get_identity_response(self, query, username, threshold=0.3, current_state="normal"):
        query = query.strip()
        if current_state == "awaiting_name_confirm":
            if "cancel" in query.lower():
                return ("I've cancelled the current action, what now?", username, "normal")
            elif any(word in query.lower() for word in ["yes","ok","alright"]):
                return ("Very well! Type in only your name below!", username, "awaiting_name")
            elif any(word in query.lower() for word in ["no","nevermind"]):
                return ("Alright then!", username, "normal")
            else:
                return ("I couldn't understand your reply, can you try again? (Yes/No/Cancel)", username, "awaiting_name_confirm")
        if current_state == "awaiting_name":
            if query.lower() == "cancel":
                return ("I've cancelled the current action, what now?", username, "normal")
            if query:
                new_name = query.strip().capitalize()
                return (f"Got it, you are {new_name}!", new_name, "normal")
            else:
                return ("I didn't quite get that, please type your name below!", username, "awaiting_name")
        
        intent, score = self._classify(query, threshold)

        if intent == "Identification":
            if username:
                return (f"You are {username}.", username, "normal")
            else:
                return ("I don't think you've told me your name yet, would you like to set it?", username, "awaiting_name_confirm")
        elif intent == "NameDirect":
            new_name = self._extract_possible_name(query)
            if new_name:
                return (f"Nice to meet you, {new_name}. I’ll remember you.", new_name, "normal")
            else:
                return ("I couldn't quite catch your name there.", username, "normal")
        elif intent == "NameChange":
            return ("Very well! Type in your name below!", username, "awaiting_name")
        elif intent == "NameDelete":
            if username:
                return (f"I’ve forgotten your name, {username}.", None, "normal")
            else:
                return ("I don’t think I know your name yet.", username, "normal")
        elif intent == "Unrecognized":
            return ("I’m not sure what you mean about your name.", username, "normal")
        elif intent == "SystemError":
            return ("[SYSTEM ERROR]: Error in identity processing.", username, "normal")
        else:
            return ("I’m not sure how to handle that request about your name.", username, "normal")