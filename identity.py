from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class IdentityManagement:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        self.name_ignore = ["call","name","my","to","please","yes","is","i","am","know","who","tell","change","want","wish","rename","switch","update","remember"]

    def _extract_possible_name(self, query):
        tokens = word_tokenize(query.lower())
        filtered = [t for t in tokens if t.isalpha() and t not in self.name_ignore and t not in self.stopwords]
        if not filtered:
            return None
        return filtered[-1].capitalize()
    
    def get_identity_response(self, query, username, subintent, current_state="normal"):
        query = query.strip()
        if current_state == "awaiting_name_confirm":
            if any(word in query.lower() for word in ["yes","ok","alright"]):
                return ("Very well! Simply tell me your name please!", username, "awaiting_name")
            elif any(word in query.lower() for word in ["no","nevermind"]):
                return ("Alright then!", username, "normal")
            else:
                return ("I couldn't understand your reply, can you try again? (Yes/No/Cancel)", username, "awaiting_name_confirm")
        elif current_state == "awaiting_name":
            if query.lower() == "cancel":
                return ("I've cancelled the current action, what now?", username, "normal")
            elif query:
                new_name = query.strip().capitalize()
                return (f"Got it, you are {new_name}!", new_name, "normal")
            else:
                return ("I didn't quite get that, please type in your name below!", username, "awaiting_name")

        if subintent == "Identification":
            if username:
                return (f"You are {username}.", username, "normal")
            else:
                return ("I don't think you've told me your name yet, would you like to set it?", username, "awaiting_name_confirm")
        elif subintent == "NameDirect":
            new_name = self._extract_possible_name(query)
            if new_name and username:
                return (f"{username}, you want to be called {new_name} now? Very well!", new_name, "normal")
            elif new_name:
                return (f"Nice to meet you, {new_name}. I’ll remember you.", new_name, "normal")
            else:
                return ("I couldn't quite catch your name there.", username, "normal")
        elif subintent == "NameChange":
            return ("Very well! Type in your name below!", username, "awaiting_name")
        elif subintent == "NameDelete":
            if username:
                return (f"I’ve forgotten your name, {username}.", None, "normal")
            else:
                return ("I don’t think I know your name yet.", username, "normal")
        elif subintent == "Unrecognized":
            return ("I’m not sure what you mean about your name.", username, "normal")
        elif subintent == "SystemError":
            return ("[SYSTEM ERROR]: Error in identity processing.", username, "normal")
        else:
            return ("I’m not sure how to handle that request about your name.", username, "normal")