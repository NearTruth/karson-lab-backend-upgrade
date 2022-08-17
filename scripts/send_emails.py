#!/usr/bin/env python

"""
module sends emails to specified receivers
for use with parse_ncdu_json.py
"""

import subprocess
import humanfriendly

MESSAGE_LENGTH = 50
SEND_INACTIVE_USERS_TO = "jbridgers"
IGNORE_USERS = ("bioapps", "jgrants", "chmay")

DEV = True  # DEV mode sends all emails to {DEV_SEND_EMAILS_TO}@bcgsc.ca
DEV_SEND_EMAILS_TO = "jbridgers"

def get_active_users():
    """
    returns the usernames of active users of karsanlab by parsing the output of getent group
    karsanlab as a set
    """

    active_users = set()
    try:
        getent_output = subprocess.run(["getent", "group", "karsanlab"], stdout.subprocess.PIPE)
        """
        sample getent output:
        group:password:groupid:user1,user2,user3,user4
        """
        active_users = set(getent_output.stdout.decode().strip().split(":")[3].split(","))
        """
        output of getent_output.stdout.decode().strip().split(":")[3].split(",") for above 
        example:
        ["user1", "user2", "user3", "user4"]
        """
        for user in IGNORE_USERS:
            active_users.discard(user)
    except Exeption:
        pass
    return active_users


def send_email(username, subject, message):
    """
    send email containing the subject and the message to {username}@bcgsc.ca

    message should contain no more than {MESSAGE_LENGTH} lines of filenames
    """
    
    if DEV: # DEV mode sends all emails to {DEV_SEND_EMAILS_TO}@bcgsc.ca
        try:
            subprocess.run(f"printf '{message}' | mail -s '{subject}' {DEV_SEND_EMAILS_TO}@bcgsc.ca",
                           shell=True)
        except Exception:  # handle exceptions
            pass
    else:
        try:  # be careful shell=True is a security risk
            subprocess.run(f"printf '{message}' | mail -s '{subject}' {username}@bcgsc.ca", shell=True)
        except Exception:  # handle exceptions
            pass


def make_dict_files_by_username(files_list):
    """
    file_list format: lst(file_metadata)

    file_metadata format: [path (str), size (str), username (str)]

    given list of files, return a dictionary with username as key and a sorted list of files as
    value
    
    output format: dict{username: lst(file)}

    """
    user_dict = {}
    for file_metadata in files_list:
        if file_metadata[2] not in user_dict:
            user_dict[file_metadata[2]] = [file_metadata]  # create key value pair
        else:
            user_dict[file_metadata[2]].append(file_metadata)  # update key value pair
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
    active user, or to {SEND_INACTIVE_USERS_TO}@bcgsc.ca if not

    sorted_files_list format: lst(file_metadata)
    file_metadata format: [path (str), size (str), username (str)]
    
    format files_list into the following way:
    subject line:
	Please review automatically marked files for {username}

	message:
	Hi {_username},
	Please review and delete unwanted files:

	file1_path (size)
	file2_path (size)
	file3_path (size)
	file4_path (size)

    if the message is too long, then the following will be appended to the message:
    This list has been truncated, please review additional emails
    

    """

    subject = f"Please review automatically marked files for {username}"
    message_header = \
    f"""Hi {username},\n
Please review and delete unwanted files:\n
"""
    message_truncated = "\nThis list has been truncated, please review additional emails. "
    line_counter = 0
    message_body = ""
    for file_metadata in sorted_files_list:
        # print(line_counter)
        message_body = message_body + f"{file_metadata[0]} ({file_metadata[1]})\n"
        line_counter = line_counter + 1
        if line_counter == MESSAGE_LENGTH and line_counter < len(sorted_files_list):
            message = message_header + message_body + message_truncated
            if active_user:
                send_email(username, subject, messagse)
            else:
                send_email(SEND_INACTIVE_USERS_TO, subject, message)
            message_body = ""
            line_counter = 0

    # send remaining message
    if message_body:
        message = message_header + message_body
        if active_user:
            send_email(username, subject, message)
        else:
            send_email(SEND_INACTIVE_USERS_TO, subject, message)



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

