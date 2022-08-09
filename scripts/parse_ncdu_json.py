#!/usr/bin/env python

"""
Parses a flattened version of a JSON created by ncdu.
Flattened JSON must be generated with `flatten.py` from `ncdu-export`
(https://github.com/wodny/ncdu-export).
"""


import argparse
import csv
import humanfriendly
import json
import os
import pwd
import stat

from datetime import datetime, timedelta

# TODO: Make the target suffixes into something configurable
INTERMEDIATE_FILE_SUFFIXES = ['sam', 'fastq', 'fq', 'mpileup']
TABLE_HEADER = ['file_path', 'size']
USERS_GROUP_ID = 100


def get_file_data(file_dict):
    """Get file name, date created, disc size, user and group owner"""
    file_name = file_dict['name']
    try:
        size = file_dict['dsize']
    except KeyError:
        # file is empty
        size = 0
    last_modified_time = datetime.fromtimestamp(file_dict['mtime'])
    user_owner = file_dict['uid']
    group_owner = file_dict['gid']
    return file_name, size, last_modified_time, user_owner, group_owner


def large_file(size, threshold):
    """Check for files greater than a size threshold"""
    if size > int(humanfriendly.parse_size(threshold, binary=True)):
        return True


def old_intermediate_file(name, date, window):
    """
    Checks if a file with an suffix defined as an intermediate file
    is older than the window
    """
    current_date = datetime.now()
    file_suffix = name.split('.')[-1]
    date_threshold = current_date - timedelta(days=window)
    if date < date_threshold and file_suffix in INTERMEDIATE_FILE_SUFFIXES:
        return True


def sort_files_list_by_size(files_list):
    """Sorts a nested list of file name and size by descending size"""
    sorted_list = sorted(
        files_list,
        key=lambda x: humanfriendly.parse_size(x[1], binary=True),
        reverse=True
    )
    return sorted_list


def write_summary_table_file(files_list, outfile_name):
    """Write file containing a table of file paths and sizes"""
    with open(outfile_name, 'w') as outfile:
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
        writer.writerow(TABLE_HEADER)
        if files_list:
            for file in sort_files_list_by_size(files_list):
                writer.writerow(file)


def get_user_owner_name(uid):
    """return the username of the uid"""
    return pwd.getpwuid(uid).pw_name


def main():
    # Parse arguments
    args = _parse_args()
    size_threshold = args.size
    days_window = int(args.days)
    input_json = args.input

    # Set initial data structures
    large_files = []
    old_intermediate_files = []
    improper_permissions_files = []
    total_space = 0

    # Parse JSON
    with open(input_json, 'r') as input_file:
        for line in input_file:
            # Load each line as a json object
            data = json.loads(line)
            try:
                # Ignore directories and symlinks
                if not stat.S_ISDIR(data['mode']) and not stat.S_ISLNK(data['mode']):
                    name, size, date, user_owner, group_owner = get_file_data(data)
                    total_space += size
                    directory = '/'.join(directory for directory in data['dirs'])
                    full_path = os.path.join(directory, name)
                    if large_file(size, size_threshold):
                        large_files.append(
                            [full_path, humanfriendly.format_size(size, binary=True)]
                        )
                    if old_intermediate_file(name, date, days_window):
                        old_intermediate_files.append(
                            [full_path, humanfriendly.format_size(size, binary=True)]
                        )
                    if group_owner == USERS_GROUP_ID:
                        # Get the owner of the file
                        username = pwd.getpwuid(user_owner).pw_name
                        improper_permissions_files.append([full_path, username])
            # Excluded paths (e.g., .snapshot) are still written to the JSON
            # But lack a "mode" key. Account for this.
            except KeyError:
                pass

    # Write the summary files
    large_files_outfile = f'{input_json}.large_files.tsv'
    write_summary_table_file(large_files, large_files_outfile)
    old_intermediate_files_outfile = f'{input_json}.old_intermediate_files_for_possible_deletion.tsv'
    write_summary_table_file(old_intermediate_files, old_intermediate_files_outfile)
    summary_outfile = f'{input_json}.summary.tsv'
    with open(summary_outfile, 'w') as outfile:
        outfile.write(
            f'Total space consumed:\t'
            f'{humanfriendly.format_size(total_space, binary=True)}\n')
    improper_permissions_outfile = f'{input_json}.files_set_to_user_group.tsv'
    with open(improper_permissions_outfile, 'w') as outfile:
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
        writer.writerow(['file_path', 'file_owner'])
        if improper_permissions_files:
            for file in improper_permissions_files:
                writer.writerow(file)


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Parses a flattened ncdu JSON file that has been '
                    'preprocessed with ncdu-export/flatten.py.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--input', '-i', help='The JSON to parse.', required=True)
    parser.add_argument(
        '--size', '-s',
        help='Size threshold in human readable format. '
             'Files greater than this size will be reported.',
        default='10GB')
    parser.add_argument(
        '--days', '-d',
        help='The number of days used as a threshold '
             'to classify old intermediate files.',
        default=30)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
