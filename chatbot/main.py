from small_talk import SmallTalkHandler

small_talk_handler = SmallTalkHandler()

# Not sure if I like this, will find out if it's problematic very soon though.
def process_user_query(query):
    query = query.lower().strip()
    if not query:
        return "JOSEFINA: Please say something!"
    small_talk_response = small_talk_handler.get_small_talk_response(query, threshold=0.1) 
    
    if small_talk_response:
        #print("SYSTEM: [Intent: Small Talk]")
        return small_talk_response
    else:
        # print("SYSTEM: [Intent: Unrecognised]")
        return "I'm sorry, I didn't understand that. You can try asking about greetings."

def main():
    print("JOSEFINA: Hello! I am Josefina, let's chat!")
    print("SYSTEM: Type 'STOP' or 'QUIT' to quit.")
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