import urllib.request
import urllib.parse
import json
import time

API_URL = "https://api.guerrillamail.com/ajax.php"
USER_AGENT = "COMP3074-Chatbot-Client"

class GuerrillaMailClient:
    def __init__(self):
        self.sid_token = None
        self.email_addr = None

    def _make_api_request(self, params):
        try:
            data = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
            req = urllib.request.Request(
                API_URL,
                data=data,
                headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body)
        except urllib.error.URLError as e:
            print(f"[SYSTEM API ERROR]: Could not connect: {e}")
            return None
        except json.JSONDecodeError:
            print("[SYSTEM API ERROR]: Failed to parse JSON response.")
            return None

    def get_email_address(self):
        print("[SYSTEM API]: Requesting new email address...")
        params = {"f": "get_email_address", "ip": "127.0.0.1", "agent": USER_AGENT}
        response = self._make_api_request(params)
        if response and "sid_token" in response:
            self.sid_token = response["sid_token"]
            self.email_addr = response["email_addr"]
            print(f"[SYSTEM API]: New email: {self.email_addr} (SID: {self.sid_token})")
            return self.sid_token, self.email_addr
        else:
            print("[SYSTEM API]: Failed to get email address.")
            return None, None

    def set_email_user(self, username):
        if not self.sid_token:
            print("[SYSTEM API]: No session token. Please call get_email_address() first.")
            return None
        print(f"[SYSTEM API]: Setting email username to '{username}'...")
        params = {
            "f": "set_email_user",
            "email_user": username,
            "sid_token": self.sid_token,
            "lang": "en"
        }
        response = self._make_api_request(params)
        if response and "email_addr" in response:
            self.email_addr = response["email_addr"]
            print(f"[SYSTEM API]: Email set successfully: {self.email_addr}")
            return response
        else:
            print("[SYSTEM API]: Failed to set email username.")
            return None

    def check_for_new_email(self):
        if not self.sid_token:
            print("[SYSTEM API]: No session token. Please call get_email_address() first.")
            return []
        print(f"[SYSTEM API]: Checking for new mail for {self.email_addr}...")
        params = {"f": "check_email", "sid_token": self.sid_token, "seq": 0}
        response = self._make_api_request(params)
        if response and "list" in response:
            emails = response["list"]
            if emails:
                print(f"[SYSTEM API]: Found {len(emails)} new email(s).")
            else:
                print("[SYSTEM API]: Inbox is empty.")
            return emails
        else:
            print("[SYSTEM API]: Failed to check email. Session may have expired.")
            return []

    def get_email_list(self, offset=0):
        if not self.sid_token:
            print("[SYSTEM API]: No session token. Please call get_email_address() first.")
            return []
        print(f"[SYSTEM API]: Fetching email list (offset={offset})...")
        params = {"f": "get_email_list", "sid_token": self.sid_token, "offset": offset}
        response = self._make_api_request(params)
        if response and "list" in response:
            emails = response["list"]
            print(f"[SYSTEM API]: Retrieved {len(emails)} email(s) from list.")
            return emails
        else:
            print("[SYSTEM API]: Failed to fetch email list.")
            return []

    def fetch_email(self, email_id):
        if not self.sid_token:
            print("[SYSTEM API]: No session token. Please call get_email_address() first.")
            return None
        print(f"[SYSTEM API]: Fetching email with ID: {email_id}...")
        params = {"f": "fetch_email", "sid_token": self.sid_token, "email_id": email_id}
        response = self._make_api_request(params)
        if response and "mail_body" in response:
            print("[SYSTEM API]: Successfully fetched email.")
            return response
        else:
            print("[SYSTEM API]: Failed to fetch email.")
            return None

    def delete_email(self, email_id):
        if not self.sid_token:
            print("[SYSTEM API]: No session token. Please call get_email_address() first.")
            return False
        print(f"[SYSTEM API]: Deleting email with ID: {email_id}...")
        params = {"f": "del_email", "sid_token": self.sid_token, "email_ids[]": [email_id]}
        response = self._make_api_request(params)
        if response and str(email_id) in response.get("deleted_ids", []):
            print("[SYSTEM API]: Email deleted successfully.")
            return True
        else:
            print("[SYSTEM API]: Failed to delete email.")
            return False

    def forget_me(self):
        if not (self.sid_token and self.email_addr):
            print("[SYSTEM API]: No active session or email to forget.")
            return False
        print(f"[SYSTEM API]: Forgetting email address: {self.email_addr}...")
        params = {"f": "forget_me", "sid_token": self.sid_token, "email_addr": self.email_addr}
        response = self._make_api_request(params)
        if response is True:
            print("[SYSTEM API]: Email address forgotten.")
            return True
        else:
            print("[SYSTEM API]: Failed to forget email address.")
            return False

    @staticmethod
    def save_email_to_file(email_data, filename="email.txt"):
        try:
            body = email_data.get("mail_body", "No content found.")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"From: {email_data.get('mail_from', 'N/A')}\n")
                f.write(f"Subject: {email_data.get('mail_subject', 'N/A')}\n")
                f.write(f"Date: {email_data.get('mail_date', 'N/A')}\n")
                f.write("-" * 20 + "\n\n")
                f.write(body)
            print(f"[SYSTEM]: Email content saved to {filename}")
        except Exception as e:
            print(f"[SYSTEM]: Could not save file: {e}")
        
# Testing Script
if __name__ == "__main__":
    gm = GuerrillaMailClient()
    sid, email = gm.get_email_address()
    if not sid:
        print("[SYSTEM]: Could not initialize Guerrilla Mail session.")
        exit(1)

    print(f"\n--- Guerrilla Mail Inbox Monitor ---")
    print(f"Temporary email address: {email}")
    print("Press Ctrl+C to stop monitoring.\n")

    try:
        seen_ids = set()
        emails = gm.get_email_list(offset=0)
        if emails:
            print(f"[SYSTEM]: Found {len(emails)} existing email(s):\n")
            for e in emails:
                seen_ids.add(e["mail_id"])
                print(f"ID: {e['mail_id']}")
                print(f"From: {e.get('mail_from', 'Unknown')}")
                print(f"Subject: {e.get('mail_subject', '(No subject)')}")
                print(f"Date: {e.get('mail_date', 'Unknown')}")
                print("-" * 40)
        else:
            print("[SYSTEM]: No emails yet.")

        #print("\n[SYSTEM]: Monitoring for new emails...\n")

        # Continuous polling loop
        while True:
            new_emails = gm.check_for_new_email()
            if new_emails:
                for e in new_emails:
                    if e["mail_id"] not in seen_ids:
                        seen_ids.add(e["mail_id"])
                        print("\n--- New Email Received ---")
                        print(f"ID: {e['mail_id']}")
                        print(f"From: {e.get('mail_from', 'Unknown')}")
                        print(f"Subject: {e.get('mail_subject', '(No subject)')}")
                        print(f"Date: {e.get('mail_date', 'Unknown')}")
                        print("-" * 40)
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n[SYSTEM]: Stopped email monitoring.")
        gm.forget_me()
        print("[SYSTEM]: Session ended cleanly.")