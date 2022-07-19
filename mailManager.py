from __future__ import print_function
from email import encoders
from service import GmailService
import base64
from email.mime.text import MIMEText
import mimetypes
import os
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class Mail:
    """
    This is a mail helper class for - 
    Checking all the mails,
    Reading a particular mail, 
    Downloading mail or attachments,
    Sending mails
    """

    service = GmailService().build_service()
    service = service.users().messages()
    data = None
    error = None

    def get_mails(self, limit=10, page=1,):
        """ 
        To get a list of all emails user wants to see

        Args:
            limit (int, optional): Number of mails user wants to see at screen in one run. Defaults to 10.
            page (int, optional): Page number according to the limit which the user wants to see (i.e., page 1 contains 'limit' number of mails). Defaults to 1.


        Changes the values of instance variable 'data' to a list of instance of message(mail) and of instance variable 'error' to any http error if occurs else None.
        """
        nextPageToken = None
        mail_list = []
        try:
            for i in range(0, page):
                messages = self.service.list(
                    userId="me", maxResults=limit, pageToken=nextPageToken, q='category:primary').execute()
                if 'nextPageToken' in messages.keys():
                    nextPageToken = messages['nextPageToken']
                else:
                    break
                
            if 'messages' in messages.keys():
                for msg in messages['messages']:
                    msg_obj = {'id': msg['id']}
                    message = self.service.get(userId="me", id=msg['id']).execute()
                    for header in message['payload']['headers']:
                        if header['name'] in ['From', 'Subject', 'Date']:
                            msg_obj[header['name']] = header['value']
                    mail_list.append(msg_obj)
            self.data, self.error = mail_list, None

        except Exception as e:
            self.data, self.error = None, e

    def get_mail(self, msg_id):
        """Using GmailApi's user.messages.get() method let's user read the complete mail

        Args:
            msg_id (str): Id of the mail which the user wants to read

        Returns:
            Instance of message (mail), which contains all details of the mail and error if any http error occurs else None
        """
        try:
            msg_obj = {}
            mail = self.service.get(
                userId='me', id=msg_id, format='raw').execute()
            msg_obj['id'] = msg_id
            msg_obj['mail_content'] = mail['snippet']
            attach = self.service.get(
                userId='me', id=msg_id, format='full', metadataHeaders=['parts']).execute()
            attach = attach['payload']['parts']
            attachments = []
            for attaches in attach:
                if attaches['filename'] != '':
                    attachment = {
                        'id': attaches['body']['attachmentId'], 'filename': attaches['filename']}
                    attachments.append(attachment)
            msg_obj['attachments'] = attachments
            return msg_obj, None
        except Exception as error:
            return None, error

    def download_attachment(self, msg_id, attachment_obj, ):
        """Downloads attchments present in the mail at the location where the command is being executed

        Args:
            msg_id (str): Id of mail from which the attachment is to be downloaded
            attachment_obj (dict): contains attchment Id and the name of the attachment which is to be downloaded 

        Returns:
            error if any http error occurs else None
        """
        try:
            attachment = self.service.attachments().get(
                userId="me", messageId=msg_id, id=attachment_obj['id']).execute()
            attachment = base64.urlsafe_b64decode(attachment['data'])
            fname = attachment_obj['filename']
            with open(fname, "wb") as binary_file:
                binary_file.write(attachment)
            return None
        except Exception as e:
            return e

    def download_mail(self, mail_id, mail_name):
        """Downloads the complete mail as .eml file in the location where the command is being executed

        Args:
            mail_id (str): Id of the mail which is to be downloaded
            mail_name (str): Name of the file with which the mail is to be downloaded

        Returns:
            1 if mail downloaded and error as None else 0 and http error
        """
        try:
            mail = self.service.get(
                userId='me', id=mail_id, format='raw').execute()
            mail = base64.urlsafe_b64decode(mail['raw'])
            data = str(mail)
            data = data.replace('\\n', '\n').replace(
                '\\r', '\r').replace('\\t', '\t').replace("\\'", "\'")
            fname = mail_name+'.eml'
            with open(fname, 'w') as f:
                f.write(data[2:-1])
            return 1, None
        except Exception as error:
            return 0, error

    def send_mail(self, to_ids, message_content, from_id=None, subject=None,  attachment=None):
        """For sending mails with GmailApi's users.messages.send() method 

        Args:
            to_ids (list(str)): All the mail Ids to whom the user wants to send the mail
            from_id (str, optional): Name of the sender. Defaults to None (if it is None then by default it will be the username from user's mail id).
            subject (str, optional): Subject of the mail. Defaults to None.
            message_content (str, optional): Body of the mail. Defaults to None.
            attachment (list(str), optional): list of filenames that are to attched with the mail. Defaults to None.

        Changes the values of instance variable 'data' to a instance of message(mail) which contains all the details of the sent mail and of instance variable 'error' to any http error if occurs else None.
        """
        try:
            sent_messages = []
            for to_id in to_ids:
                mime_message = MIMEMultipart()
                mime_message['To'] = to_id
                mime_message['From'] = from_id
                mime_message['Subject'] = subject
                text_part = MIMEText(message_content)
                mime_message.attach(text_part)
                file_attach = attachment
                for attaches in file_attach:
                    content_type, encoding = mimetypes.guess_type(attaches)
                    main_type, sub_type = content_type.split('/', 1)
                    file_name = os.path.basename(attaches)
                    f = open(attaches, 'rb')
                    if f == None:
                        raise Exception(
                            "File {} does not exist".format(attaches))
                    myFile = MIMEBase(main_type, sub_type)
                    myFile.set_payload(f.read())
                    myFile.add_header('Content-Disposition',
                                      'attachment', filename=file_name)
                    encoders.encode_base64(myFile)
                    f.close()
                    mime_message.attach(myFile)

                encoded_message = base64.urlsafe_b64encode(
                    mime_message.as_bytes()).decode()
                create_msg = {
                    'raw': encoded_message
                }
                send_message = (self.service.send
                                (userId='me', body=create_msg)).execute()
                sent_messages.append(send_message)
            self.data, self.error = sent_messages, None
        except Exception as e:
            self.data, self.error = None, e
