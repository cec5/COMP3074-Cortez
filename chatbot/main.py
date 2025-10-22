from intent_classifier import IntentClassifier
from small_talk import SmallTalkHandler 

intent_classifier = IntentClassifier() 
small_talk_handler = SmallTalkHandler() 

session_context = {
    'name': None
}

def process_user_query(query):
    query = query.lower().strip()
    if not query:
        return "JOSEFINA: Please say something!"
    intent, score = intent_classifier.classify(query, threshold=0.2)

    if intent == "SmallTalk":
        return small_talk_handler.get_small_talk_response(query, threshold=0.1)     
    elif intent == "IdentityManagement":
        return f"SYSTEM: [Intent: Identity Management]"
    elif intent == "Discoverability":
        return f"SYSTEM: [Intent: Discoverability]"
    elif intent == "QuestionAnswering":
        return f"SYSTEM: [Intent: Question Answering]"
    elif intent == "Unrecognised":
        return "SYSTEM: [Intent Unrecognised]" 
    else:
        return "SYSTEM: [ERROR]: Internal Classification Issue"

def main():
    print("JOSEFINA: Hello! I am Josefina,let's chat!")
    print("SYSTEM: Type 'STOP' or 'QUIT' to quit")
    stop = False
    while not stop:
        try:
            user_input = input("USER: ")
            if user_input.upper().strip() in ["STOP", "QUIT"]:
                stop = True
                print("JOSEFINA: I'm shutting down, until next time!")
            else:
                response = process_user_query(user_input)
                print(f"JOSEFINA: {response}")
        except KeyboardInterrupt:
            stop = True
            print("\nSYSTEM: Force quit")

if __name__ == '__main__':
    main()
