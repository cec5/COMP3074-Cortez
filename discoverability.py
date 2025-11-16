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

class Discoverability:
    def __init__(self, data_path="datasets/discoverability.csv"):
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        self.intent_phrases_tfidf = None
        self.phrases = []
        self.intents = []
        self.stopwords = set(stopwords.words('english'))
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
            print(f"[SYSTEM ERROR]: Error loading discoverability dataset: {e}")
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
    
    def get_discoverability_response(self, query, threshold=0.3, current_state="normal"):
        query = query.strip()
        intent, score = self._classify(query, threshold)
        if current_state == "general_help_loop":
            if "cancel" in query.lower():
                return ("I've cancelled the current action, what now?", "normal")
            elif query.lower() == "where am i" or query.lower() == "where am i?":
                return ("You are currently in the general help menu. You can elaborate further or cancel the action.", "general_help_loop")
            elif any(word in query.lower() for word in ["no","nevermind"]):
                return ("Alright then, let's move on!", "normal")
            elif any(word in query.lower() for word in ["commands","command"]):
                intent = "HelpCommands"
            elif any(word in query.lower() for word in ["identification","name","identity"]):
                intent = "Identification"
            elif any(word in query.lower() for word in ["capable","capabilities","do"]):
                intent = "Capabilities"
            else:
                return ("I couldn't understand your reply, can you try again?", "general_help_loop")
        elif current_state == "capabilities_help":
            if "cancel" in query.lower():
                return ("I've cancelled the current action, what now?", "normal")
            elif query.lower() == "where am i" or query.lower() == "where am i?":
                return ("You are currently in the capabilities help menu. You can ask me for further information about my capabilties.", "capabilities_help")
            elif any(word in query.lower() for word in ["no","nevermind"]):
                return ("Alright then, let's move on!", "normal")
            elif any(word in query.lower() for word in ["yes","ok","alright"]):
                return ("Alright, ask me about small talk, question and answering, identification, or email services for more information.", "capabilities_help")
            elif any(word in query.lower() for word in ["small","talk","talking","conversation","chat","chatting"]):
                return ("I'm happy to have small talk if you if that's is what you would like, just talk to me!", "normal")
            elif any(word in query.lower() for word in ["question","questions","answer","answers","answering"]):
                return ("I have a wide variety of knowledge! Ask me something and I'll do my best to answer it!", "normal")
            elif any(word in query.lower() for word in ["identification","name","identity"]):
                intent = "Identification"
            elif any(word in query.lower() for word in ["email","emails"]):
                return ("I am capable of generating you a temporary email for use! As well as managing emails recieved at that address, if you wish to get started, ask me to generate you an email!", "normal") 
            else:
                return ("I couldn't understand your reply, can you try again?", "capabilities_help")

        if intent == "HelpGeneral":
            return ("What do you need help with? Would you like further information on commands, identification, or my capabilities?", "general_help_loop")
        if intent == "HelpCommands":
            return ("I have two universal commands:\nCANCEL: cancels any ongoing action\nWHERE AM I: tells you what state the chatbot current is in", "normal")
        elif intent == "Identification":
            return ("If you tell me your name or tell me that you want to set your name, I am capable of remembering it. You can also change your name, or tell me to forget it entirely.", "normal")
        elif intent == "Capabilities":
            return ("I am capable of basic small talk, question and answering, identity management, and generating you a temporary email, would you like any further information on any of these?", "capabilities_help")
        elif intent == "SystemError":
            return ("[SYSTEM ERROR]: Error in discoverability processing.", "normal")
        else:
            return ("I unfortunately can't understand what you are asking for help with.", "normal")
