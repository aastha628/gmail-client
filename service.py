from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailService:
    """ 
    validates credentials, 
    take permissions,
    build service
    """

    SCOPES = ['https://mail.google.com/']

    def build_service(self):
        """
        validates credentials, take permissions, build service

        Args: 
            None
        Returns:
            A Resource object with methods for interacting with the service 

        """
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file(
                'token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        try:
            # create gmail api client
            service = build('gmail', 'v1', credentials=creds)
        except Exception as error:
            service = None

        return service
