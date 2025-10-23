from intent_classifier import IntentClassifier
from small_talk import SmallTalkHandler 

intent_classifier = IntentClassifier() 
small_talk_handler = SmallTalkHandler() 

def process_user_query(query):
    query = query.lower().strip()
    if not query:
        return "JOSEFINA: Please say something!"
    intent, score = intent_classifier.classify(query, threshold=0.2)

    if intent == "SmallTalk":
        return small_talk_handler.get_small_talk_response(query, threshold=0.2)     
    elif intent == "IdentityManagement":
        return "SYSTEM: [Intent: Identity Management]"
    elif intent == "Discoverability":
        return "SYSTEM: [Intent: Discoverability]"
    elif intent == "QuestionAnswering":
        return "SYSTEM: [Intent: Question Answering]"
    elif intent == "Unrecognised":
        return "JOSEFINA: Forgive me, but I'm unable to process what are you saying." 
    else:
        return "SYSTEM: Error with internal classification"

def main():
    print("SYSTEM: Type 'STOP' or 'QUIT' to quit")
    print("JOSEFINA: Hello! I am Josefina, let's chat!")
    stop = False
    while not stop:
        try:
            user_input = input("USER: ")
            if user_input.upper().strip() in ["STOP", "QUIT"]:
                stop = True
                print("JOSEFINA: I'm shutting down, until next time!")
            else:
                response = process_user_query(user_input)
                print(f"{response}")
        except KeyboardInterrupt:
            stop = True
            print("\nSYSTEM: Force quit")

if __name__ == '__main__':
    main()