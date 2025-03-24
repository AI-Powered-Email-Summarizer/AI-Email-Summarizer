import os
import base64
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup  # Import for removing HTML tags
from transformers import pipeline


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Load the Hugging Face Summarization Model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


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

def decode_email_body(payload):
    """Extracts and decodes the email body"""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" or part["mimeType"] == "text/html":
                data = part["body"].get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                if part["mimeType"] == "text/html":
                    body = BeautifulSoup(body, "html.parser").get_text()  # Remove HTML tags
    elif "body" in payload:
        data = payload["body"].get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8")
    
    return body.strip()

def summarize_email(content):
    """Summarizes the email content using Hugging Face model."""
    if len(content) < 50:  # If the content is too short, return as is
        return content
    summary = summarizer(content[:1024], max_length=100, min_length=30, do_sample=False)  # Summarize first 1024 chars
    return summary[0]["summary_text"]

def fetch_emails():
    service = authenticate_gmail()
    email_data = []
    next_page_token = None

    while len(email_data) < 10:  # Fetch up to 10 emails
        results = service.users().messages().list(
            userId="me", labelIds=["INBOX"], maxResults=10, pageToken=next_page_token).execute()

        messages = results.get("messages", [])
        if not messages:
            break  # No more messages

        for msg in messages:
            if len(email_data) >= 10:  # Stop when we have 10 emails
                break
            msg_details = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_details["payload"]["headers"]
            payload = msg_details["payload"]

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            body = decode_email_body(payload)
            summary = summarize_email(body)
            snippet = msg_details.get("snippet", "No Snippet Available")

            email_data.append({
                "subject": subject,
                "sender": sender,
                "summary": summary,
                "snippet": snippet
            })

        next_page_token = results.get("nextPageToken")  # Move to next page
        if not next_page_token:
            break  # No more pages

    return email_data



def classify_email(subject):
    important_keywords = ["urgent", "meeting", "deadline", "project", "important"]
    
    for word in important_keywords:
        if word.lower() in subject.lower():
            return "Important"
    return "Other"

if __name__ == "__main__":
    emails = fetch_emails()
    for email in emails:
        print(f"From: {email['sender']}\nSubject: {email['subject']}\nSummary: {email['summary']}\n{'-'*40}")
