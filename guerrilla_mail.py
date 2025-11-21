import requests
import time
import os
import json

class GuerrillaSession:
    
    API_URL = "https://api.guerrillamail.com/ajax.php"

    def __init__(self, sid_token=None, lang='en'):
        self.session = requests.Session()
        self.lang = lang
        self.sid_token = sid_token
        self.email_addr = None
        self.email_timestamp = None
        self.alias = None
        self.inbox = []
        
        try:
            if sid_token:
                params = {'sid_token': self.sid_token, 'lang': self.lang}
                response = self._api_call('get_email_address', params, method='GET')
                if response and 'auth' in response and 'error_codes' in response['auth'] and 'auth-session-not-initialized' in response['auth']['error_codes']:
                    self.sid_token = None
                    self._start_new_session()
                elif response:
                    self._update_session_details(response)
                else:
                    self.sid_token = None
                    self._start_new_session()
            else:
                self._start_new_session()
        except requests.RequestException as e:
            print(f"Error initializing session: {e}")
            raise

    def _start_new_session(self):
        params = {'lang': self.lang}
        self.sid_token = None 
        response = self._api_call('get_email_address', params, method='GET')
        if response:
            self._update_session_details(response)
        else:
            print("FATAL: Could not start new session. API might be down.")
            raise ConnectionError("Failed to initialize a new session.")

    def _update_session_details(self, response_json):
        if not isinstance(response_json, dict):
            return

        self.sid_token = response_json.get('sid_token', self.sid_token)
        self.email_addr = response_json.get('email_addr', self.email_addr)
        self.email_timestamp = response_json.get('email_timestamp', self.email_timestamp)
        self.alias = response_json.get('alias', self.alias)
        
        if 'list' in response_json:
            existing_ids = {email['mail_id'] for email in self.inbox}
            new_emails = [email for email in response_json['list'] if email['mail_id'] not in existing_ids]
            self.inbox = new_emails + self.inbox
            self.inbox.sort(key=lambda x: int(x.get('mail_timestamp', 0)), reverse=True)

    def _api_call(self, func_name, params=None, method='GET'):
        if params is None:
            params = {}

        if isinstance(params, dict):
            params_list = list(params.items())
        else:
            params_list = list(params) 

        if 'f' not in [p[0] for p in params_list]:
            params_list.append(('f', func_name))
            
        if self.sid_token and 'sid_token' not in [p[0] for p in params_list]:
            params_list.append(('sid_token', self.sid_token))

        try:
            if method.upper() == 'GET':
                response = self.session.get(self.API_URL, params=params_list, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(self.API_URL, data=params_list, timeout=10)
            else:
                raise ValueError("Method must be 'GET' or 'POST'")

            response.raise_for_status()
            response_json = response.json()
            
            if 'sid_token' in response_json and response_json['sid_token'] != self.sid_token:
                self.sid_token = response_json['sid_token']
            
            self._update_session_details(response_json)
            return response_json

        except requests.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} for URL: {e.response.url}")
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response: {response.text}")
            
        return None 

    def get_inbox_list(self, offset=0):
        response = self._api_call('get_email_list', {'offset': str(offset)})
        if response and 'list' in response:
            return self.format_inbox_list()
        return "I couldn't fetch your inbox from the mail server."

    def check_new_emails(self):
        seq = 0
        if self.inbox:
            seq = max(int(email.get('mail_id', 0)) for email in self.inbox)
        
        response = self._api_call('check_email', {'seq': str(seq)})
        
        if response and 'list' in response:
            new_emails = response['list']
            if not new_emails:
                return "No new mail."
            
            formatted_list = "--- New Mail ---\n"
            for i, email in enumerate(new_emails, 1):
                subject = email.get('mail_subject', 'No Subject')
                sender = email.get('mail_from', 'Unknown Sender')
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(email.get('mail_timestamp', 0))))
                formatted_list += f"[{i}] {subject} - From: {sender} ({timestamp})\n"
            return formatted_list
        return "I couldn't check for new mail right now."

    def format_inbox_list(self):
        if not self.inbox:
            return "Your inbox is currently empty."
        
        formatted_list = "--- Current Inbox ---\n"
        for i, email in enumerate(self.inbox, 1):
            subject = email.get('mail_subject', 'No Subject')
            sender = email.get('mail_from', 'Unknown Sender')
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(email.get('mail_timestamp', 0))))
            read_status = " (Read)" if email.get('mail_read', '0') == '1' else " (Unread)"
            formatted_list += f"[{i}] {subject} - From: {sender} ({timestamp}){read_status}\n"
        return formatted_list

    def _get_email_ids_from_indices(self, indices_str):
        if not self.inbox:
            return []
            
        indices_to_process = set()
        max_index = len(self.inbox)
        
        if indices_str.lower() == 'all':
            return [email['mail_id'] for email in self.inbox]
            
        parts = indices_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if start < 1: start = 1
                    if end > max_index: end = max_index
                    indices_to_process.update(range(start - 1, end)) # 0-based index
                except ValueError:
                    continue # Silently ignore invalid ranges
            else:
                try:
                    index = int(part)
                    if 1 <= index <= max_index:
                        indices_to_process.add(index - 1) # 0-based index
                except ValueError:
                    continue # Silently ignore invalid indices
                    
        mail_ids = [self.inbox[i]['mail_id'] for i in sorted(list(indices_to_process))]
        return mail_ids

    def fetch_email_body(self, index):
        try:
            index_int = int(index)
            if not (1 <= index_int <= len(self.inbox)):
                return f"Error: Index {index_int} is out of bounds (1-{len(self.inbox)})."
        except ValueError:
            return f"Error: Index must be a number."
            
        mail_id = self.inbox[index_int - 1]['mail_id']
        
        response = self._api_call('fetch_email', {'email_id': mail_id})
        
        if response and 'mail_body' in response:
            self.inbox[index_int - 1]['mail_read'] = '1'
            return response
        return f"Error: Could not fetch email ID {mail_id}."

    def delete_emails(self, indices_str):
        mail_ids = self._get_email_ids_from_indices(indices_str)
        if not mail_ids:
            return "You either have no emails, or you didn't provide a valid index."
            
        params = [('email_ids[]', mid) for mid in mail_ids]
        response = self._api_call('del_email', params=params, method='POST')
        
        if response and 'deleted_ids' in response:
            deleted_ids_set = set(response['deleted_ids'])
            self.inbox = [email for email in self.inbox if email['mail_id'] not in deleted_ids_set]
            return f"Successfully deleted {len(deleted_ids_set)} email(s)."
        return "I failed to delete those emails. Please try again."

    def download_emails(self, indices_str):
        mail_ids = self._get_email_ids_from_indices(indices_str)
        if not mail_ids:
            return "You either have no emails, or you didn't provide a valid index."
            
        save_dir = self.sid_token
        os.makedirs(save_dir, exist_ok=True)
        
        downloaded_files = []
        failed_files = 0
        
        for mail_id in mail_ids:
            index = next((i for i, email in enumerate(self.inbox) if email['mail_id'] == mail_id), -1)
            
            if index == -1:
                failed_files += 1
                continue

            email_data = self.fetch_email_body(index + 1) # 1-based index
            
            if isinstance(email_data, dict) and 'mail_body' in email_data:
                subject = email_data.get('mail_subject', 'no_subject').replace(' ', '_')
                subject = "".join(c for c in subject if c.isalnum() or c in ('_', '-')).rstrip()
                filename = f"{mail_id}_{subject[:30]}.html"
                filepath = os.path.join(save_dir, filename)
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(email_data['mail_body'])
                    downloaded_files.append(filepath)
                except IOError as e:
                    print(f"Error writing file {filepath}: {e}") # Console log for dev
                    failed_files += 1
            else:
                failed_files += 1
                
        return f"Successfully downloaded {len(downloaded_files)} emails to the '{save_dir}' folder."

    def get_email_data_for_view(self, index):
        return self.fetch_email_body(index)

    def set_new_email(self, local_part):
        if not local_part:
            return "You need to provide a name, like 'set my-test-email'."
            
        params = {'email_user': local_part, 'lang': self.lang}
        response = self._api_call('set_email_user', params, method='POST')
        
        if response and 'email_addr' in response:
            old_email = self.email_addr
            self.inbox = [] 
            return f"Done! Your email has been changed from {old_email} to {self.email_addr}."
        return "I couldn't set that email address. It might be taken or invalid."

    def forget_current_email(self):
        if not self.email_addr:
            return "There's no active email address to forget."
            
        params = {'email_addr': self.email_addr}
        response = self._api_call('forget_me', params, method='POST')
        
        if response:
            self.email_addr = None
            self.email_timestamp = None
            self.alias = None
            self.inbox = []
            return "Okay, I've forgotten your old email address."
        return "I failed to forget that email. Please try again."
        
    def end_session(self):
        self.sid_token = None
        self.email_addr = None
        self.email_timestamp = None
        self.alias = None
        self.inbox = []