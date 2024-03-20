from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from typing import Any, Dict, Match, Optional
import os.path
import re
import time


class Gmail:

    __SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    __Client: Resource


    def __enter__(self):
        credentials: Optional[Credentials] = None

        if os.path.exists("gmail_token.json"):
            credentials = Credentials.from_authorized_user_file("gmail_token.json", self.__SCOPES)

        if credentials is None or not credentials.valid:
            if credentials is not None and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                credentials = InstalledAppFlow.from_client_secrets_file("gmail_credentials.json", self.__SCOPES).run_local_server(port=0)

            with open("gmail_token.json", "w") as file:
                file.write(credentials.to_json())
                file.close()

        self.__Client = build("gmail", "v1", credentials=credentials)

        return self


    def __exit__(self, *_):
        pass


    def get_code(self, email: str) -> str:
        start: float = time.time()

        while time.time() - start < 15:
            messages: Dict[str, Any] = self.__Client.users().messages().list(q=f"to:{email}", userId="me").execute()

            for temp in (messages["messages"] if "messages" in messages else []):
                message: Dict[str, Any] = self.__Client.users().messages().get(id=temp["id"], userId="me").execute()

                subject: str = [header["value"] for header in message["payload"]["headers"] if header["name"] == "Subject"][0]
                if subject == "Your ESPN Account Passcode":
                    result: Optional[Match] = re.search(r"Here is your one-time ESPN account passcode: (\d+)", message["snippet"])
                    if result is None:
                        raise Exception(f"{email}: Could Not Find Passcode in Email: {message['snippet']}")

                    return str(result.group(1))

            time.sleep(1)

        raise Exception(f"{email}: Failed to Find Passcode Email")
