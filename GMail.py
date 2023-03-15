from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional
from utils import LOGGER
import os.path
import re
import time

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def login():
    creds = None

    if os.path.exists("gmail_token.json"):
        creds = Credentials.from_authorized_user_file("gmail_token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("gmail_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("gmail_token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_code(email: str) -> str:
    gmail = login()
    retry = True

    while retry:
        code = __get_code_from_email(gmail, email)
        if code is not None:
            return code

        LOGGER.warning(f"{email}: Code Not Found, Waiting...")
        time.sleep(2)


def __get_code_from_email(gmail, email: str) -> Optional[str]:
    messages = gmail.users().messages().list(userId="me").execute().get("messages", [])

    for message in reversed(messages):
        message = gmail.users().messages().get(id=message["id"], userId="me").execute()

        subject = [header for header in message["payload"]["headers"] if header["name"] == "Subject"]
        assert len(subject) == 1
        if subject[0]["value"] != "Your ESPN Account Passcode":
            continue

        to = [header for header in message["payload"]["headers"] if header["name"] == "To"]
        assert len(to) == 1
        if to[0]["value"] != email:
            continue

        passcodeSearch = re.search(r"Here is your one-time ESPN account passcode: (\d+)", message["snippet"])
        if passcodeSearch is None:
            raise Exception("Could Not Find Passcode")

        return str(passcodeSearch.group(1))

    return None
