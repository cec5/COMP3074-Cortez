from intent_classifier import IntentClassifier
from small_talk import SmallTalkHandler
from question_answer import QAHandler

intent_classifier = IntentClassifier() 
small_talk_handler = SmallTalkHandler()
qa_handler = QAHandler()

def process_user_query(query):
    query = query.lower().strip()
    if not query:
        return "JOSEFINA: Please say something!"
    intent, score = intent_classifier.classify(query, threshold=0.2)

    if intent == "SmallTalk":
        return small_talk_handler.get_small_talk_response(query, threshold=0.2)     
    elif intent == "IdentityManagement":
        return "SYSTEM: [Intent: Identity Management]"
    elif intent == "QuestionAnswering":
        return qa_handler.get_QA_response(query, threshold=0.5)
    elif intent == "Unrecognized":
        return "JOSEFINA: Forgive me, but I'm unable to recognize what you are saying." 
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