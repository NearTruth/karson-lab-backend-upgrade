import send_emails
import humanfriendly

def create_long_files_list():
    """
    [path, size, username]
    """
    files_list = []
    for i in range(51):
        files_list.append([f"a/b/{i}", humanfriendly.format_size(i*1000, binary=True), "user1"])
    for i in range(70):
        files_list.append(
            [f"a/c/{i}", humanfriendly.format_size(i * 1000, binary=True), "user2"])
    return files_list

def create_short_files_list():
    """
    [path, size, username]
    """
    files_list = []
    for i in range(40):
        files_list.append([f"a/b/{i}", humanfriendly.format_size(i*1000, binary=True), "user1"])
    for i in range(1):
        files_list.append(
            [f"a/c/{i}", humanfriendly.format_size(i * 1000, binary=True), "user2"])
    return files_list

def create_long_sorted_files_list_one_user():
    """
    {username: [path, size, username]}
    """
    dict = {
        "user1": []
    }
    for i in range(60):
        dict["user1"].append([f"a/b/{i}", humanfriendly.format_size(i*1000, binary=True), "user1"])
    return dict


def test_make_user_dict():
    print(send_emails.make_dict_files_by_username(create_files_list()))

def test_format_and_send_email_long():
    dict = create_long_sorted_files_list_one_user()
    for user in dict:
        send_emails.format_and_send_email(user, send_emails.sort_files_list_by_size(dict[user]),
                                          active_user=False)

def test_email_from_list_long():
    lst = create_long_files_list()
    send_emails.send_emails_from_files_list(lst)

def test_email_from_list_short():
    lst = create_short_files_list()
    send_emails.send_emails_from_files_list(lst)

def test_multiple_lists():
    lst1 = create_long_files_list()
    lst2 = create_short_files_list()
    send_emails.send_emails_from_files_list(lst1, lst2)


test_multiple_lists()
