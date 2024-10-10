#!/usr/bin/env python3
# coding=<utf-8>

""" Program to send GET requests to the EU CELLAR endpoint and download zip files for the given documents under a CELLAR URI."""

import os
import io
from datetime import datetime
import logging

import requests
import zipfile

from utils.file_utils import get_subdir_list_from_path, print_list_to_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ids_to_download(id_list, dir_to_check):
    """
    Check whether the id in the given CELLAR id_list is already present
    in the directory containing previously downloaded files.
    The directory contains subdirectories named with a cellar id.
    Return a list of cellar_ids absent from the subdirectory names.

    :param id_list: list
    :return: list
    """
    try:
        downloaded_files_list = get_subdir_list_from_path(dir_to_check)
        missing_ids_list = list(set(id_list) - set(downloaded_files_list))
        logging.info(f"Missing ids: {len(missing_ids_list)}")
        
        # Log downloaded files and missing ids
        in_dir_name = 'id_logs/in_dir_lists/'
        os.makedirs(os.path.dirname(in_dir_name), exist_ok=True)
        print_list_to_file(in_dir_name + 'in_dir_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt', downloaded_files_list)
        
        new_ids_dir_name = 'id_logs/cellar_ids/'
        os.makedirs(os.path.dirname(new_ids_dir_name), exist_ok=True)
        print_list_to_file(new_ids_dir_name + 'cellar_ids_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt', missing_ids_list)
        
        return missing_ids_list
    except Exception as e:
        logging.error(f"Error checking ids to download: {e}")
        return []

def rest_get_call(id):
    """Send a GET request to download a zip file for the given id under the CELLAR URI."""
    try:
        url = f'http://publications.europa.eu/resource/cellar/{id}'
        headers = {
            'Accept': "application/zip;mtype=fmx4, application/xml;mtype=fmx4, application/xhtml+xml, text/html, text/html;type=simplified, application/msword, text/plain, application/xml;notice=object",
            'Accept-Language': "eng",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "publications.europa.eu"
        }
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"Error sending GET request: {e}")
        return None

def extract_zip(response, folder_path):
    """
    Downloads the zip file returned by the restful get request.
    Source: https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    """
    try:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(folder_path)
    except Exception as e:
        logging.error(f"Error downloading zip: {e}")

def process_range(sub_list, folder_path):
    """
    Process a list of ids to download the corresponding zip files.

    :param sub_list: list of str
    :param folder_path: str
    :return: write to files
    """
    try:
        zip_files = []
        single_files = []
        other_downloads = []
        
        for id in sub_list:
            sub_folder_path = folder_path + id
            
            response = rest_get_call(id.strip())
            if response is None:
                continue
            
            if 'Content-Type' in response.headers:
                if 'zip' in response.headers['Content-Type']:
                    zip_files.append(id)
                    extract_zip(response, sub_folder_path)
                else:
                    single_files.append(id)
                    
                    out_file = sub_folder_path + '/' + id + '.html'
                    os.makedirs(os.path.dirname(out_file), exist_ok=True)
                    with open(out_file, 'w+', encoding="utf-8") as f:
                        f.write(response.text)
            else:
                other_downloads.append(id)
        
        # Log results
        id_logs_path = 'id_logs/failed_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt'
        os.makedirs(os.path.dirname(id_logs_path), exist_ok=True)
        with open(id_logs_path, 'w+') as f:
            if len(other_downloads) != 0:
                f.write('Failed downloads ' + datetime.now().strftime("%Y%m%d-%H%M%S") + '\n' + str(other_downloads))
            # HEre it would be good to log the files that were downloaded and the files that were not. In general it would be a good place to log WebAPI metadata information about the documents
        
        logging.info(f"Zip files: {len(zip_files)}, Single files: {len(single_files)}, Failed downloads: {len(other_downloads)}")
    except Exception as e:
        logging.error(f"Error processing range: {e}")