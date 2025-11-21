class Discoverability:
    def get_discoverability_response(self, query, subintent, current_state="normal"):
        query = query.strip()
        if current_state == "general_help_loop":
            if any(word in query.lower() for word in ["no","nevermind"]):
                return ("Very well.", "normal")
            elif any(word in query.lower() for word in ["commands","command"]):
                subintent = "HelpCommands"
            elif any(word in query.lower() for word in ["identification","name","identity"]):
                subintent = "Identification"
            elif any(word in query.lower() for word in ["capable","capabilities","do"]):
                subintent = "Capabilities"
            elif any(word in query.lower() for word in ["yes", "affirmative"]):
                return ("I can certaintly tell you more, just specifiy what you would me to elaborate on! Commands, identification, or my capabilities?", "general_help_loop")
            else:
                return ("I couldn't understand your reply, do you still need general help?", "general_help_loop")
        elif current_state == "capabilities_help":
            if any(word in query.lower() for word in ["no","nevermind"]):
                return ("Very well.", "normal")
            elif any(word in query.lower() for word in ["yes","ok","alright"]):
                return ("Alright, ask me about small talk, question and answering, identification, or email services for more information.", "capabilities_help")
            elif any(word in query.lower() for word in ["small","talk","talking","conversation","chat","chatting"]):
                return ("I'm happy to have small talk if you if that's is what you would like, just talk to me!", "normal")
            elif any(word in query.lower() for word in ["question","questions","answer","answers","answering"]):
                return ("I have a wide variety of knowledge! Ask me something and I'll do my best to answer it!", "normal")
            elif any(word in query.lower() for word in ["identification","name","identity"]):
                subintent = "Identification"
            elif any(word in query.lower() for word in ["email","emails"]):
                return ("I am capable of generating you a temporary email for use! As well as managing emails recieved at that address, if you wish to get started, ask me to generate you an email!", "normal") 
            else:
                return ("I couldn't understand your reply, do you still need regarding my capabilities?", "capabilities_help")

        if subintent == "HelpGeneral":
            return ("What do you need help with? Would you like any further information on commands, identification, or my capabilities?", "general_help_loop")
        elif subintent == "HelpCommands":
            return ("I have three universal commands:\nWHERE AM I: tells you what state the chatbot current is in.\nGO BACK: Rewinds to the last step\nCANCEL: cancels any ongoing action in its entirety", "normal")
        elif subintent == "Identification":
            return ("If you tell me your name or tell me that you want to set your name, I am capable of remembering it. You can also change your name, or tell me to forget it entirely.", "normal")
        elif subintent == "Capabilities":
            return ("I am capable of basic small talk, question and answering, identity management, and generating you a temporary email, would you like any further information on any of these?", "capabilities_help")
        elif subintent == "Purpose":
            return ("I am Maila, an AI-powered Chatbot designed for a class at the University of Nottingham. I am designed to assist you with setting up a temporarily email address in an conversational manner.", "normal")
        else:
            return ("I unfortunately can't understand what you are asking for help with.", "normal")
