from intent_classifier import IntentClassifier
from small_talk import SmallTalkHandler
from question_answer import QAHandler
from identity import IdentityManagement

intent_classifier = IntentClassifier() 
small_talk_handler = SmallTalkHandler()
qa_handler = QAHandler()
identity_handler = IdentityManagement()

username = None

def process_user_query(query):
    global username
    query = query.lower().strip()
    if not query:
        return "JOSEFINA: Please say something!"

    intent, score = intent_classifier.classify(query, threshold=0.2)

    if intent == "SmallTalk":
        return small_talk_handler.get_small_talk_response(query, threshold=0.4)     
    elif intent == "IdentityManagement":
        response, updated_name = identity_handler.get_identity_response(query, username, threshold=0.3)
        username = updated_name
        return response
    elif intent == "QuestionAnswering":
        return qa_handler.get_QA_response(query, threshold=0.65)
    elif intent == "Unrecognized":
        return "JOSEFINA: Forgive me, but I'm unable to recognize what you are saying." 
    else:
        return "SYSTEM: Error with internal classification"

def main():
    global username
    print("SYSTEM: Type 'STOP' or 'QUIT' to quit")
    print("JOSEFINA: Hello! I am Josefina, let's chat!")
    stop = False
    while not stop:
        try:
            prompt_label = username.upper() if username else "USER"
            user_input = input(f"{prompt_label}: ")
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