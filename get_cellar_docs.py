#!/usr/bin/env python3
# coding=<utf-8>

""" Program to send GET requests to the EU CELLAR endpoint and download zip files for the given documents under a CELLAR URI."""

import os
import io
from datetime import datetime

import requests
import zipfile

from utils.file_utils import get_subdir_list_from_path, print_list_to_file 

# Set current time and date
timestamp = str(datetime.now().strftime("%Y%m%d-%H%M%S"))

def check_ids_to_download(id_list, dir_to_check):
    """
    Check whether the id in the given CELLAR id_list is already present
    in the directory containing previously downloaded files.
    The directory contains subdirectories named with a cellar id.
    Return a list of cellar_ids absent from the subdirectory names.

    :param id_list: list
    :return: list
    """

    # Get CELLAR ids in the subdirectories containing the files already downloaded
    downloaded_files_list = get_subdir_list_from_path(dir_to_check)
    # print('ALREADY_DOWNLOADED:', len(downloaded_files_list))
    in_dir_name = 'id_logs/in_dir_lists/'
    os.makedirs(os.path.dirname(in_dir_name), exist_ok=True)
    print_list_to_file(in_dir_name + 'in_dir_' + timestamp + '.txt', downloaded_files_list)

    # Get list of files that have not yet been downloaded
    missing_ids_list = list(set(id_list) - set(downloaded_files_list))
    #print('SET_DIFF:', len(missing_ids_list))
    new_ids_dir_name = 'id_logs/cellar_ids/'
    os.makedirs(os.path.dirname(new_ids_dir_name), exist_ok=True)
    print_list_to_file(new_ids_dir_name + 'cellar_ids_' + timestamp + '.txt', missing_ids_list)

    return missing_ids_list


def rest_get_call(id):
    """Send a GET request to download a zip file for the given id under the CELLAR URI."""

    url = 'http://publications.europa.eu/resource/cellar/' + id

    headers = {
        'Accept': "application/zip;mtype=fmx4, application/xml;mtype=fmx4, application/xhtml+xml, text/html, text/html;type=simplified, application/msword, text/plain, application/xml;notice=object",
        'Accept-Language': "eng",
        'Content-Type': "application/x-www-form-urlencoded",
        'Host': "publications.europa.eu"#,
    }

    response = requests.request("GET", url, headers=headers)

    return response


def download_zip(response, folder_path):
    """
    Downloads the zip file returned by the restful get request.
    Source: https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    """
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(folder_path)


def process_range(sub_list, folder_path):
    """
    Process a list of ids to download the corresponding zip files.

    :param sub_list: list of str
    :param folder_path: str
    :return: write to files
    """

    # Keep track of downloads
    zip_files = []
    single_files = []
    other_downloads = []

    # Count downloads
    count_cellar_ids = 0
    count_zip = 0
    count_single= 0
    count_other = 0

    for id in sub_list:
        count_cellar_ids += 1

        # Specify sub_folder_path to send results of request
        sub_folder_path = folder_path + id

        # Send Restful GET request for the given id
        response = rest_get_call(id.strip())

        # If the response's header contains the string 'Content-Type'
        if 'Content-Type' in response.headers:

            # If the string 'zip' appears as a value of 'Content-Type'
            if 'zip' in response.headers['Content-Type']:

                count_zip += 1
                zip_files.append(id)

                # Download the contents of the zip file in the given folder
                download_zip(response, sub_folder_path)

            # If the value of 'Content-Type' is not 'zip'
            else:
                count_single += 1
                single_files.append(id)

                # Create a directory with the cellar_id name
                # and write the returned content in a file
                # with the same name
                out_file = sub_folder_path + '/' + id + '.html'
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                with open(out_file, 'w+', encoding="utf-8") as f:
                    f.write(response.text)

        # If the response's header does not contain the string 'Content-Type'
        else:
            count_other += 1
            other_downloads.append(id)
            # print('NO_CONTENT_TYPE:', response.content)

            #  Write the returned content in a file
            # out_file = sub_folder_path + '/' + id + '.xml'
            # with open(out_file, 'wb') as f:
            #     f.write(response.text)

    # log_text = ("\nQuery file: " + __file__ +
    #             "\nDownload date: " + str(datetime.today()) +
    #             "\n\nNumber of zip files downloaded: " + str(count_zip) +
    #             "\nNumber of non-zip files downloaded: " + str(count_single) +
    #             "\nNumber of other downloads: " + str(count_other) +
    #             "\nTotal number of cellar ids processed: " + str(count_zip + count_single + count_other) +
    #             "\n\nTotal number of downloaded files: " + str(count_zip + count_single) +
    #             "\nTotal number of cellar ids: " + str(len(id_list)) +
    #             "\n\n========================================\n"
    #             )
    #
    # print(log_text)

    # Write the list of other (failed) downloads in a file
    id_logs_path = 'id_logs/failed_' + timestamp + '.txt'
    os.makedirs(os.path.dirname(id_logs_path), exist_ok=True)
    with open(id_logs_path, 'w+') as f:
        if len(other_downloads) != 0:
            f.write('Failed downloads ' + timestamp + '\n' + str(other_downloads))
