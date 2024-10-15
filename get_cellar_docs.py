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
LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = 'http://publications.europa.eu/resource/cellar/'
LOG_DIR = 'id_logs/'

def get_current_timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def check_ids_to_download(id_list: list, dir_to_check: str) -> list:
    """Check whether the id in the given CELLAR id_list is already present
    in the directory containing previously downloaded files."""

    try:
        downloaded_files_list = get_subdir_list_from_path(dir_to_check)
        missing_ids_list = list(set(id_list) - set(downloaded_files_list))
        return missing_ids_list
    except Exception as e:
        logging.error(f"Error checking ids to download: {e}")
        return []

def log_downloaded_files(downloaded_files: list, dir_to_check: str):
    """Log downloaded files."""
    in_dir_name = LOG_DIR + 'in_dir_lists/'
    os.makedirs(os.path.dirname(in_dir_name), exist_ok=True)
    print_list_to_file(in_dir_name + 'in_dir_' + get_current_timestamp() + '.txt', downloaded_files)

def log_missing_ids(missing_ids: list):
    """Log missing ids."""
    new_ids_dir_name = LOG_DIR + 'cellar_ids/'
    os.makedirs(os.path.dirname(new_ids_dir_name), exist_ok=True)
    print_list_to_file(new_ids_dir_name + 'cellar_ids_' + get_current_timestamp() + '.txt', missing_ids)

def rest_get_call(id: str) -> requests.Response:
    """Send a GET request to download a zip file for the given id under the CELLAR URI."""
    try:
        url = BASE_URL + id
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

def extract_zip(response: requests.Response, folder_path: str):
    """
    Downloads the zip file returned by the restful get request.
    Source: https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    """
    try:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(folder_path)
    except Exception as e:
        logging.error(f"Error downloading zip: {e}")

def process_single_file(response: requests.Response, folder_path: str, id: str):
    """Process a single file."""
    out_file = folder_path + '/' + id + '.html'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w+', encoding="utf-8") as f:
        f.write(response.text)

def process_range(ids: list, folder_path: str):
    """Process a list of ids to download the corresponding zip files."""
    try:
        zip_files = []
        single_files = []
        other_downloads = []
        
        for id in ids:
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
                    process_single_file(response, sub_folder_path, id)
            else:
                other_downloads.append(id)
        
        # Log results
        id_logs_path = LOG_DIR + 'failed_' + get_current_timestamp() + '.txt'
        os.makedirs(os.path.dirname(id_logs_path), exist_ok=True)
        with open(id_logs_path, 'w+') as f:
            if len(other_downloads) != 0:
                f.write('Failed downloads ' + get_current_timestamp() + '\n' + str(other_downloads))
        
        logging.info(f"Zip files: {len(zip_files)}, Single files: {len(single_files)}, Failed downloads: {len(other_downloads)}")
    except Exception as e:
        logging.error(f"Error processing range: {e}")