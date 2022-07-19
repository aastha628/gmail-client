import os
import time
import sys
from typing import List
from threading import Thread
from service import GmailService
from drafts import Drafts
from mailManager import Mail
from labels import Labels, LabelVisibility, MsgVisibility
import typer
from rich import box
from rich.console import Console
from rich.table import Table
from progress import ProgressBar

service = GmailService()
console = Console()
app = typer.Typer()
progress_bar = ProgressBar()
mails_obj = Mail()
label_obj = Labels()


def show_menu(start, end, retry):
    """let's user input the choice (when asked for) and checks its correctness .

    Args:
        start (int): starting index of the menu
        end (int): end index of the menu
        retry (int): number of retries left for the user

    Returns:
        choice(int): choice entered by the user
    """
    choice = 0
    while retry > 0:
        console.print(
            "[bold yellow]Enter a choice between {} and {}[/bold yellow]: ".format(start, end), end="")
        try:
            choice = int(input())
        except:
            choice = -1
        if start <= choice <= end:
            return choice
        retry -= 1
        error_handler("Out of index!! {} retries left".format(retry))


def error_handler(error):
    console.print(
        "[bold red]\n⚠️  Error Occured: {}!![/bold red]\n".format(error))


def create_table(headers, data, box=box.SQUARE):
    """Generates and Prints the table in the terminal with the help rich library

    Args:
        headers (list(str)): List of headings of all columns
        data (list(list(str))): List of lists of all column values of a row 
        box (object of box class, optional): Type of box(outer boundary) of the table. Defaults to box.SQUARE.
    """
    table = Table(show_header=True, header_style="bold green",
                  show_lines=True, box=box)
    for column in headers:
        style = None
        if column == '#':
            style = 'dim'
        table.add_column(column, style=style, justify="center")
    for row in data:
        table.add_row(*tuple(row))
    console.print('\n')
    console.print(table)
    console.print("\n")


def read_mail(mail_content):
    """Shows user the complete contents of the mail

    Args:
        mail_content (dict): Contains details about the mail - id, from, date, subject

    Returns:
        Message(mail) object
    """

    msg_obj, error = mails_obj.get_mail(mail_content['id'])
    if error != None:
        raise error
    msg_obj['From'] = mail_content['From']
    msg_obj['Date'] = mail_content['Date']
    msg_obj['Subject'] = mail_content['Subject']

    data = [['FROM: '+msg_obj['From']], ['DATE: ' + msg_obj['Date']],
            ['SUBJECT: '+msg_obj['Subject']], ['BODY: ' + msg_obj['mail_content']]]
    attach_data = []

    for i in range(len(msg_obj['attachments'])):
        attach_data.append([str(i+1), msg_obj['attachments'][i]['filename']])

    attach_files = str()
    attach_files += "Attachment: "
    for files in attach_data:
        attach_files += files[0]
        attach_files += ". "
        attach_files += files[1]
        attach_files += "\n"
    attachment_data = [attach_files]
    if msg_obj['attachments']:
        data.append(attachment_data)
    header = ['Mail Content']
    create_table(header, data, box=box.DOUBLE_EDGE)

    return msg_obj


@app.command(short_help='To create a draft')
def draft(body: str, to: str = None, by: str = None, subject: str = None, attachment: List[str] = []):
    """Creates and save a draft as per user's requirements with the help of Drafts class 

    Args:
        body (str): Body of the draft
        to (str, optional): Receiver's mail id. Defaults to None.
        by (str, optional): Sender's name. Defaults to None.
        subject (str, optional): Subject of the draft. Defaults to None.
        attachment (List[str], optional): Attachment filenames. Defaults to [].
    """
    for a in attachment:
        if os.path.getsize(a) >25000000:
            error_handler("File size exceeded limit")
            return
    draft_obj = Drafts()
    draft, error = draft_obj.create_draft(to, by, subject, body, attachment)
    if error == None:
        header = ['DraftId', 'To', 'By', 'Subject', 'Body', 'Attachment']
        if attachment:
            attachment = "✔"
        else:
            attachment = "✘"
        data = [[draft['id'], to, by, subject, body, attachment]]
        console.print("\n ✅", "[bold green]Draft Created[/bold green]\n")
        create_table(header, data)
    else:
        error_handler(error)


@app.command(short_help='To see list of emails')
def check_mails(limit: int = 10, page: int = 1):
    """To get a list of all mails within the limit

    Args:
        limit (int, optional): Number of mails user wants to see at screen in one run. Defaults to 10.
        page (int, optional): Page number according to the limit which the user wants to see (i.e., page 1 contains 'limit' number of mails). Defaults to 1.

    Returns:
        List of instance of message(mail)
    """

    thread = Thread(target=mails_obj.get_mails, args=(limit, page))
    thread.start()
    progress_bar.start()
    thread.join()
    progress_bar.end()

    mails, error = mails_obj.data, mails_obj.error

    if error == None:
        header = ['#', 'Id', 'From', 'Date', 'Subject']
        data = []
        for idx, mail in enumerate(mails, 1):
            data.append([str(idx), mail['id'], mail['From'],
                        mail['Date'], mail['Subject']])
        create_table(header, data)
        return mails
    else:
        error_handler(error)


@app.command(short_help='To send mails')
def send_mail(to: List[str], body: str, by: str = None, subject: str = None,   attachment: List[str] = []):
    """Send mails with the help mailManager.py library, prints success or error.

    Args:
        to (List[str]): list of receiver ids
        body (str): body of the mail
        by (str, optional): sender's name. Defaults to None.
        subject (str, optional): subject of the mail. Defaults to None.
        attachment (List[str], optional): filenames of attachments. Defaults to [].
    """
    for a in attachment:
        if os.path.getsize(a) >25000000:
            error_handler("File size exceeded limit")
            return
    thread = Thread(target=mails_obj.send_mail,
                    args=(to, body, by, subject,  attachment))
    thread.start()
    progress_bar.start()
    thread.join()
    progress_bar.end()

    sent_data, error = mails_obj.data, mails_obj.error

    if error == None:
        header = ['MailId', 'To', 'By', 'Subject', 'Body', 'Attachment']
        data = []
        if attachment:
            attachment = "✔"
        else:
            attachment = "✘"
        for i in range(len(sent_data)):
            data.append([sent_data[i]['id'], to[i],
                        by, subject, body, attachment])
        console.print("\n ✅", "[bold green]Mail Sent[/bold green]\n")
        create_table(header, data)
    else:
        error_handler(error)


@app.command(short_help='To download mail or attachments')
def download(limit: int = 10, page: int = 1):
    """To download the complete mail or attachments 

    Args:
        limit (int, optional): Number of mails user wants to see at screen in one run. Defaults to 10.
        page (int, optional): Page number according to the limit which the user wants to see (i.e., page 1 contains 'limit' number of mails). Defaults to 1.

    """
    try:
        mails_data = check_mails(limit, page)

        s_num = show_menu(1, limit, 5)
        if s_num == None:
            return
        mail_selected = mails_data[s_num-1]
        msg_obj = read_mail(mail_selected)

        if msg_obj['attachments']:
            console.print(
                "\n[bold yellow]Choose from following options:\n1 -> To download the mail \n2 -> To download the attachment \n[/bold yellow]")
            d_num = show_menu(1, 2, 2)
            if d_num == None:
                return
        else:
            console.print(
                "[bold yellow]To download the mail [Y/N]? [/bold yellow]", end="")
            d_num = input(" ")

        if d_num == 1 or d_num == 'Y' or d_num == 'y':
            console.print(
                "[bold yellow]Give File a name (without any extension): [/bold yellow]", end="")
            fname = input(" ")
            success, error = mails_obj.download_mail(msg_obj['id'], fname)

            if error == None:
                console.print(
                    "\n ✅", "[bold green]Mail Downloaded[/bold green]\n")
            else:
                error_handler(error)
        elif d_num == 2:
            console.print(
                "[bold yellow]Give Attachment numbers to download: [/bold yellow]", end="")
            a_num = input("\t")
            a_num = a_num.split(" ")
            for i in a_num:
                try:
                    if int(i) > len(msg_obj['attachments']):
                        error_handler("Out of index")
                    else:
                        error = mails_obj.download_attachment(
                            msg_obj['id'], msg_obj['attachments'][int(i)-1])
                except:
                    error = "Invalid argument"
                if error == None:
                    console.print(
                        "\n ✅", "[bold green]Attachment Downloaded[/bold green]\n")
                else:
                    error_handler(error)
        else:
            console.print("\n[bold cyan]Exiting the window[/bold cyan]\n")
    except Exception as e:
        error_handler(e)


@app.command(short_help='To see the list of all existing labels')
def list_labels():
    """Prints a list of all labels present in user's gmail account with the help of labels.py module
    """
    labels, error = label_obj.label_list()
    labels_list = labels['labels']
    header = ['Label Id', 'Label Name',
              'Label List Visibility', 'Message List Visibilty']
    data = []
    Eachlabel = []
    for labelObj in labels_list:
        if 'labelListVisibility' not in labelObj:
            labelObj['labelListVisibility'] = " "
        if 'messageListVisibility' not in labelObj:
            labelObj['messageListVisibility'] = " "
        Eachlabel = [labelObj['id'], labelObj['name'],
                     labelObj['labelListVisibility'], labelObj['messageListVisibility']]
        data.append(Eachlabel)
    create_table(header, data)


@app.command(short_help='To create labels')
def create_label(label_name: str, label_visibility: LabelVisibility = None, msglist_visibility: MsgVisibility = None):
    """Create a new label according to user's needs

   Args:
        label_name (str): name of the label
        label_visibility (str, optional): It has three options - LabelShow, LabelShowIfUnread, LabelHide. Defaults to None.
        messagelist_visibility (str, optional): It has two options - Show or Hide. Defaults to None.

    Prints "label created" or if error occured
    """
    label, error = label_obj.create_label(
        label_name, label_visibility, msglist_visibility)
    if error == None:
        console.print("\n ✅", "[bold green]Label Created[/bold green]\n")
    else:
        error_handler(error)


@app.command(short_help='To add mail to a label')
def modify_mail(limit: int = 10, page: int = 1):
    """For changing (adding or removing) the labels of a mail

    Args:
        limit (int, optional): Number of mails user wants to see at screen in one run. Defaults to 10.
        page (int, optional): Page number according to the limit which the user wants to see (i.e., page 1 contains 'limit' number of mails). Defaults to 1.
    """
    mails_list = check_mails(limit, page)
    s_num = show_menu(1, limit, 5)
    if s_num == None:
        return
    mail_selected = mails_list[s_num-1]
    msg_obj = read_mail(mail_selected)

    console.print(
        "[bold yellow] Give label names to add: [/bold yellow]", end="")
    add_labels = input(" ")
    add_labels = add_labels.split(" ")
    console.print(
        "[bold yellow] Give label names to remove or can be left blank: [/bold yellow]", end="")
    remove_labels = input(" ")
    remove_labels = remove_labels.split(" ")

    modify, error = label_obj.mail_to_label(
        msg_obj['id'], add_labels, remove_labels)
    if error == None:
        console.print("\n ✅", "[bold green]Mail modified[/bold green]\n")
    else:
        error_handler(error)


@app.command(short_help='To switch user')
def switch_user():
    """
    To change the current user by changing the token
    Args:
        None

    """
    if os.path.exists("token.json"):
        os.remove('token.json')
    build = service.build_service()
    if build != None:
        console.print("\n ✅", "[bold green]User Switched[/bold green]\n")
    else:
        error_handler("Something went wrong....")


@app.command(short_help='To log out of the app')
def log_out():
    """Logs out the user by removing the token file

    Args:
        None
    """
    if os.path.exists("token.json"):
        os.remove('token.json')
    console.print("\n ✅", "[bold green]User Logged Out![/bold green]\n")


if __name__ == "__main__":
    app()
