from __future__ import print_function
from service import GmailService
import base64
import mimetypes
import os
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError


class Drafts:
    """
    Build complete messages from information given,
    Creates drafts
    """

    service = GmailService().build_service()
    service = service.users().drafts()

    def create_draft(self, to_id=None, from_id=None, subject=None, message_content=None,
                     attachments=[]):
        """Create and insert a draft email with attachment.

        Args: 
            Gmail Id of the reciever: list(str)
            Name of sender: str
            Subject of the mail: str 
            Body of the mail: str
            Attachments (if any): list(str)

        Returns: Draft object (including draft id and message meta data) and Error 
        """
        try:
            mime_message = MIMEMultipart()
            mime_message['To'] = to_id
            mime_message['From'] = from_id
            mime_message['Subject'] = subject
            text_part = MIMEText(message_content)
            mime_message.attach(text_part)
            for attaches in attachments:
                content_type, encoding = mimetypes.guess_type(attaches)
                main_type, sub_type = content_type.split('/', 1)
                file_name = os.path.basename(attaches)

                f = open(attaches, 'rb')
                if f == None:
                    raise Exception("File {} does not exist".format(attaches))

                myFile = MIMEBase(main_type, sub_type)
                myFile.set_payload(f.read())
                myFile.add_header('Content-Disposition',
                                  'attachment', filename=file_name)
                encoders.encode_base64(myFile)
                f.close()
                mime_message.attach(myFile)

            encoded_message = base64.urlsafe_b64encode(
                mime_message.as_bytes()).decode()

            create_draft_request_body = {
                'message': {
                    'raw': encoded_message
                }
            }
            draft = self.service.create(userId="me",
                                        body=create_draft_request_body).execute()
            return draft, None
        except Exception as error:
            return None, error
