# main.py
import os
from datetime import datetime
from threading import Thread

from get_cellar_ids import get_cellar_info_from_endpoint, get_cellar_ids_from_json_results, cellar_ids_to_file, get_cellar_ids_from_csv_file
from get_text_from_cellar_files import get_text
from get_cellar_docs import check_ids_to_download, process_range

from utils.file_utils import text_to_str, to_json_output_file

QUERY_FILE = 'queries/sparql_queries/generic.rq'
SPARQL_QUERY_RESULTS_DIR = "queries/sparql_query_results/"
DIR_TO_CHECK = "data/cellar_files/"
DOWNLOAD_DIR = "data/cellar_files/{}"
TXT_FOLDER_PATH = "data/text_files/"

def get_sparql_query_results():
    sparql_query = text_to_str(QUERY_FILE)
    print('SPARQL_PATH:', sparql_query)
    return get_cellar_info_from_endpoint(sparql_query)

def output_sparql_results(sparql_query_results):
    sparql_query_results_file = os.path.join(SPARQL_QUERY_RESULTS_DIR, "query_results.json")
    os.makedirs(os.path.dirname(SPARQL_QUERY_RESULTS_DIR), exist_ok=True)
    to_json_output_file(sparql_query_results_file, sparql_query_results)    

import os

def check_ids_to_download(cellar_ids):
    if DIR_TO_CHECK and os.path.exists(DIR_TO_CHECK):
        # Check which files have already been downloaded
        downloaded_ids = [filename.split('.')[0] for filename in os.listdir(DIR_TO_CHECK) if filename.endswith('.xml') or filename.endswith('.html')]
        # Return the IDs of the files that have not been downloaded yet
        return [cellar_id for cellar_id in cellar_ids if cellar_id not in downloaded_ids]
    return cellar_ids

def download_files(cellar_ids):
    nthreads = 11
    threads = []
    download_dir = DIR_TO_CHECK
    for i in range(nthreads):  
        sub_list = cellar_ids[i::nthreads]
        t = Thread(target=process_range, args=(sub_list, os.path.join(download_dir, str(i))))
        threads.append(t)
    [t.start() for t in threads]
    [t.join() for t in threads]

def main():

    # Query the OP SPARQL endpoint
    sparql_query_results = get_sparql_query_results()
    output_sparql_results(sparql_query_results)

    # Get CELLAR IDs
    cellar_ids = sorted(get_cellar_ids_from_json_results(sparql_query_results))
    cellar_ids_to_file(cellar_ids)

    # Verify whether there are new documents to download
    cellar_ids = check_ids_to_download(cellar_ids)
    print('NEW_FILES_TO_DOWNLOAD:', len(cellar_ids))
    
    # Create the download directory if it doesn't exist
    download_dir = DIR_TO_CHECK
    os.makedirs(download_dir, exist_ok=True)

    # Download the documents from CELLAR REST APIs   
    download_files(cellar_ids)

    # Extract the text from the HTML documents
    txt_folder_path = TXT_FOLDER_PATH  
    get_text(download_dir, txt_folder_path, replace_existing=False)

if __name__ == "__main__":
    main()