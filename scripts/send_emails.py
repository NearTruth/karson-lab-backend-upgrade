#!/usr/bin/env python

"""
module sends emails to specified receivers
for use with parse_ncdu_json.py
"""

import pwd
import subprocess
import humanfriendly

MESSAGE_LENGTH = 100
INACTIVE_USER = "jbridgers"
IGNORE_USERS = ("bioapps", "jgrants", "chmay")


def get_active_users():
    """
    returns the usernames of active users of karsanlab by parsing the output of getent group
    karsanlab as a set
    """
    users = set()
    try:
        getent_output = subprocess.run(["getent", "group", "karsanlab"], stdout.subprocess.PIPE)
        users = set(getent_output.stdout.decode().strip().split(":")[3].split(","))
        for user in IGNORE_USERS:
            users.discard(user)
    except Exeption:
        pass
    return users


def get_user_owner_name(uid):
    """return the username of the uid"""
    return pwd.getpwuid(uid).pw_name


def send_email(username, subject, message):
    """
    send email containing the subject and the message to {username}@bcgsc.ca

    message should contain no more than 100 lines of filenames
    """
    # subject = f"Files automatically marked for deletion for {username}"
    try:  # be careful shell=True is a security risk
        subprocess.run(f"echo '{message}' | mail -s '{subject}' {username}@bcgsc.ca", shell=True)
    except Exception:  # handle exceptions
        pass


def make_dict_files_by_uid(file_list):
    """
    input format: lst([path, size, uid])
    given list of files, return a dictionary with uid as key and a list of files as value
    output format: dict{uid: lst(file)}
    """
    user_dict = {}
    for f in file_list:
        if f[2] not in user_dict:
            user_dict[f[2]] = [f]  # create key value pair
        else:
            user_dict[f[2]].append(f)  # update key value pair
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
        if line_counter < MESSAGE_LENGTH:
            message_body = message_body + f"{f[0]} ({f[1]})\n"
            line_counter = line_counter + 1
        else:  # line_counter == MESSAGE_LENGTH
            message = message_header + message_body
            if active_user:
                send_email(username, subject, message)
            else:
                send_email(INACTIVE_USER, subject, message)
                
            message = ""
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
    for files_list in files_lists:
        if files_list:
            files_dict = make_dict_files_by_uid(files_list)  # index files by user
            active_users = get_active_users()  # get active users of karsan lab
            for uid in files_dict:
                username = get_user_owner_name(uid)  # get username
                files_dict[uid] = sort_files_list_by_size(files_dict[uid])  # sort list
                format_and_send_email(username, files_dict[uid], username in active_users)
                # send emails

                

