import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

from intent_classifier import IntentClassifier
from small_talk import SmallTalkHandler
from question_answer import QAHandler
from identity import IdentityManagement
from discoverability import Discoverability

BG_COLOR = "#ece5dd"
CHAT_BG = "#ffffff"
BOT_COLOR = "#ffffff"
USER_COLOR = "#dcf8c6"
TEXT_COLOR = "#111b21"
TIME_COLOR = "#667781"
BUTTON_BG = "#128c7e"
BUTTON_FG = "#ffffff"
FONT = ("Helvetica", 11)
FONT_BOLD = ("Helvetica", 11, "bold")

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Maila Chatbot")
        self.root.geometry("420x600")
        self.root.configure(bg=BG_COLOR)
        self.username = None
        self.chat_state = "normal"
        self.intent_classifier = IntentClassifier()
        self.small_talk_handler = SmallTalkHandler()
        self.qa_handler = QAHandler()
        self.identity_handler = IdentityManagement()
        self.discoverability_handler = Discoverability()
        self.create_widgets()
        self.add_chat_message("Hello! I am Maila, let's chat!", "bot")

    def create_widgets(self):
        self.chat_frame = tk.Frame(self.root, bg=CHAT_BG, bd=0)
        self.chat_frame.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
        self.chat_history = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            bg=CHAT_BG,
            fg=TEXT_COLOR,
            font=FONT,
            relief=tk.FLAT,
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        self.chat_history.tag_configure("user_bubble", background=USER_COLOR, justify='right', lmargin1=80, lmargin2=80, rmargin=10, spacing1=3, spacing2=1, spacing3=3)
        self.chat_history.tag_configure("bot_bubble", background=BOT_COLOR, justify='left', lmargin1=10, lmargin2=10, rmargin=80, spacing1=3, spacing2=1, spacing3=3)
        self.chat_history.tag_configure("user_name", justify='right', font=FONT_BOLD, foreground="#000000", spacing1=6, spacing3=2)
        self.chat_history.tag_configure("bot_name", justify='left', font=FONT_BOLD, foreground="#000000", spacing1=6, spacing3=2)
        self.chat_history.tag_configure("timestamp_right", justify='right', foreground=TIME_COLOR, font=("Helvetica", 8), spacing1=2, spacing3=6)
        self.chat_history.tag_configure("timestamp_left", justify='left', foreground=TIME_COLOR, font=("Helvetica", 8), spacing1=0, spacing3=6)
        input_frame = tk.Frame(self.root, bg=BG_COLOR, pady=6)
        input_frame.pack(fill=tk.X, padx=10)
        self.user_input = tk.Entry(
            input_frame,
            font=FONT,
            bg="#ffffff",
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground="#cccccc",
            highlightcolor="#cccccc"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8))
        self.user_input.bind("<Return>", self.on_send_pressed)
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            relief=tk.FLAT,
            activebackground="#075e54",
            activeforeground="#ffffff",
            command=self.on_send_pressed
        )
        self.send_button.pack(side=tk.RIGHT, ipadx=10, ipady=6)

    def on_send_pressed(self, event=None):
        query = self.user_input.get().strip()
        if not query:
            return
        self.user_input.delete(0, tk.END)
        self.add_chat_message(query, "user")
        self.root.after(200, self.get_bot_response, query) # makes it realistic I guess?

    def add_chat_message(self, message, sender):
        self.chat_history.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        if sender == "user":
            name = self.username.upper() if self.username else "YOU"
            self.chat_history.insert(tk.END, f"{name}\n", "user_name")
            self.chat_history.insert(tk.END, f"{message}\n", "user_bubble")
            self.chat_history.insert(tk.END, f"{timestamp}\n", "timestamp_right")
        else:
            self.chat_history.insert(tk.END, "MAILA\n", "bot_name")
            self.chat_history.insert(tk.END, f"{message}\n", "bot_bubble")
            self.chat_history.insert(tk.END, f"{timestamp}\n", "timestamp_left")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def get_bot_response(self, query): # Check if this is acceptable for context tracking
        if query.lower == "cancel":
            if self.chat_state == "normal":
                response = "There is no ongoing action to cancel."
            else:
                self.chat_state = "normal"
                response = "I've cancelled the ongoing action, what now?" 
        elif self.chat_state in ["awaiting_name", "awaiting_name_confirm"]:
            response_text, new_name, new_state = self.identity_handler.get_identity_response(query, self.username, subintent="none", current_state=self.chat_state)
            self.chat_state = new_state
            self.username = new_name
            response = response_text
        elif self.chat_state in ["general_help_loop", "capabilities_help"]:
            response_text, new_state = self.discoverability_handler.get_discoverability_response(query, subintent="none", current_state=self.chat_state)
            response = response_text
            self.chat_state = new_state
        else:
            intent, subintent, score = self.intent_classifier.classify(query, threshold=0.2)
            if query.lower() == "where am i" or query.lower() == "where am i?":
                response = "The chatbot is currently in a normal state, there is no ongoing action."
            elif intent == "SmallTalk":
                raw_response = self.small_talk_handler.get_small_talk_response(query, threshold=0.4)
                if "{username}" in raw_response:
                    name_to_insert = self.username if self.username else "friend"
                    response = raw_response.replace("{username}", name_to_insert)
                else:
                    response = raw_response
            elif intent == "IdentityManagement":
                response_text, new_name, new_state = self.identity_handler.get_identity_response(query, self.username, subintent=subintent, current_state="normal")
                self.username = new_name
                self.chat_state = new_state
                response = response_text
            elif intent == "QuestionAnswering":
                response = self.qa_handler.get_QA_response(query, threshold=0.65)
            elif intent == "Discoverability":
                response_text, new_state = self.discoverability_handler.get_discoverability_response(query, subintent=subintent, current_state="normal")
                self.chat_state = new_state
                response = response_text
            elif intent == "Unrecognized":
                response = "Forgive me, but I'm unable to recognize what you are saying."
            else:
                response = "[SYSTEM ERROR]: An internal classification error occurred."
        self.add_chat_message(response, "bot")

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()