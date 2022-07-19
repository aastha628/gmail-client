from __future__ import print_function
from service import GmailService
from email.mime.text import MIMEText
from service import GmailService
from enum import Enum


class MsgVisibility(str, Enum):
    mshow = 'Show'
    mhide = 'Hide'


class LabelVisibility(str, Enum):
    lshow = 'LabelShow'
    lshowunread = 'LabelShowIfUnread'
    lhide = 'LabelHide'


class Labels:
    """
    Creating labels,
    To see complete list of labels,
    Changing the labels of mails
    """

    service = GmailService().build_service()
    labels = service.users().labels()
    messages = service.users().messages()

    def label_list(self):
        """
        Using GmailApi's users.labels method finds out all the labels present

        Args:
            None

        Returns:
            List of Label objects (including label id, name, messageListVisibility, labelListVisibility, and type) and Error
        """
        try:
            labels_list = self.labels.list(userId="me").execute()
            return labels_list, None
        except Exception as error:
            return None, error

    def create_label(self, label_name, label_visibility=None, messagelist_visibility=None):
        """Creates labels according to the parameters

        Args:
            label_name (str): name of the label
            label_visibility (str, optional): It has three options - LabelShow, LabelShowIfUnread, LabelHide. Defaults to None.
            messagelist_visibility (str, optional): It has two options - Show or Hide. Defaults to None.

        Returns:
            Instance of label, that contains all the details about it and error
        """
        try:
            body = {
                "labelListVisibility": label_visibility,
                "messageListVisibility": messagelist_visibility,
                "name": label_name
            }
            label = self.labels.create(userId="me", body=body).execute()
            return label, None
        except Exception as error:
            return None, error

    def mail_to_label(self, mail_id, add_labels, remove_labels=None):
        """For changing (adding or removing) the labels of a mail

        Args:
            mail_id (str): Id of the mail
            add_labels (list(str)): list of all labels to which the mail is to be added.
            remove_labels (list(str), optional): list of all labels from which the mail is to be removed. Defaults to None.

        Returns:
            Instance of message(mail), that contains all details about it and error
        """
        try:
            labels_list, error_list = self.label_list()
            add_Ids = []
            remove_Ids = []

            for label_name in add_labels:
                for l_name in labels_list['labels']:
                    if label_name.upper() == l_name['name']:
                        add_Ids.append(l_name['id'])

            for label_name in remove_labels:
                for l_name in labels_list['labels']:
                    if label_name.upper() == l_name['name']:
                        remove_Ids.append(l_name['id'])

            body = {
                "addLabelIds": add_Ids,
                "removeLabelIds": remove_Ids
            }
            modify = self.messages.modify(
                userId="me", id=mail_id, body=body).execute()
            return modify, None

        except Exception as error:
            return None, error
