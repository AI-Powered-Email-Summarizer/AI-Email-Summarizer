import os
import base64
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    token_path = "token.pickle"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def fetch_unread_emails():
    """Fetch unread emails from Gmail."""
    service = authenticate_gmail()
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
    messages = results.get("messages", [])

    email_data = []
    for msg in messages[:10]:  # Fetch up to 10 emails
        msg_details = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_details["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        snippet = msg_details.get("snippet", "No Preview Available")
        
        email_data.append({"subject": subject, "sender": sender, "snippet": snippet})
    
    return email_data

if __name__ == "__main__":
    emails = fetch_unread_emails()
    for email in emails:
        print(f"From: {email['sender']}\nSubject: {email['subject']}\nSnippet: {email['snippet']}\n{'-'*40}")
