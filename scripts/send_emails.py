#!/usr/bin/env python

"""
module sends emails to specified receivers
for use with parse_ncdu_json.py
"""

import subprocess
import humanfriendly

MESSAGE_LENGTH = 50
INACTIVE_USER = "jbridgers"
IGNORE_USERS = ("bioapps", "jgrants", "chmay")

DEV = True
TEST_ACTIVE_USER_SET = set()

def get_active_users():
    """
    returns the usernames of active users of karsanlab by parsing the output of getent group
    karsanlab as a set
    """
    
    if DEV: # DEV mode turns off shell calls and prints emails to stdout
        return TEST_ACTIVE_USER_SET
    else:
        users = set()
        try:
            getent_output = subprocess.run(["getent", "group", "karsanlab"], stdout.subprocess.PIPE)
            users = set(getent_output.stdout.decode().strip().split(":")[3].split(","))
            for user in IGNORE_USERS:
                users.discard(user)
        except Exeption:
            pass
        return users


def send_email(username, subject, message):
    """
    send email containing the subject and the message to {username}@bcgsc.ca

    message should contain no more than 100 lines of filenames
    """
    
    if DEV: # DEV mode turns off shell calls and prints emails to stdout
        print(f"printf '{message}' | mail -s '{subject}' {username}@bcgsc.ca")
    else:
        try:  # be careful shell=True is a security risk
            subprocess.run(f"printf '{message}' | mail -s '{subject}' {username}@bcgsc.ca", shell=True)
        except Exception:  # handle exceptions
            pass


def make_dict_files_by_username(file_list):
    """
    input format: lst([path, size, username])
    given list of files, return a dictionary with username as key and a sorted list of files as
    value
    output format: dict{username: lst(file)}
    """
    user_dict = {}
    for f in file_list:
        if f[2] not in user_dict:
            user_dict[f[2]] = [f]  # create key value pair
        else:
            user_dict[f[2]].append(f)  # update key value pair
    for username in user_dict:
        user_dict[username] = sort_files_list_by_size(user_dict[username])  # sort list
    return user_dict


def sort_files_list_by_size(files_list):
    """Sorts a nested list of file name and size by descending size"""
    sorted_list = sorted(
        files_list,
        key=lambda x: humanfriendly.parse_size(x[1], binary=True),
        reverse=True
    )
    return sorted_list


def format_and_send_email(username, sorted_files_list, active_user=True):
    """
    format the subject and message then send the email to {username}@bcgsc.ca if the user is an
    active user, or to {INACTIVE_USER}@bcgsc.ca if not

    sorted_files_list format: lst([file_path, size, uid])

    format files_list into the following way
    subject line:
	Files automatically marked for deletion for {_username}

	message:
	Hi {_username},
	please review and delete unwanted files:

	file1_path (size)
	file2_path (size)
	file3_path (size)
	file4_path (size)
    """

    subject = f"Files automatically marked for deletion for {username}"
    message_header = \
    f"""Hi {username},\n
please review and delete unwanted files:\n
"""
    line_counter = 0
    message_body = ""
    for f in sorted_files_list:
        # print(line_counter)
        message_body = message_body + f"{f[0]} ({f[1]})\n"
        line_counter = line_counter + 1
        if line_counter == 50:  # line_counter == MESSAGE_LENGTH
            message = message_header + message_body
            if active_user:
                send_email(username, subject, message)  # send message of MESSAGE_LENGTH lines
            else:
                send_email(INACTIVE_USER, subject, message)
            message_body = ""
            line_counter = 0

    # send remaining message
    message = message_header + message_body
    if active_user:
        send_email(username, subject, message)
    else:
        send_email(INACTIVE_USER, subject, message)



def send_emails_from_files_list(*files_lists):
    # reads files_lists as a tuple containing various file_lists
    """
    given file_list, group files by user using a dictionary, sort each list in the dictionary by 
    size, check that the username is an active user in karsanlab, format email subject and 
    message, then send the email
    """
    active_users = get_active_users()  # get active users of karsan lab
    for files_list in files_lists:
        if files_list:
            files_dict = make_dict_files_by_username(files_list)  # index files by user
            for username in files_dict:
                format_and_send_email(username, files_dict[username], username in active_users)
                # send emails

