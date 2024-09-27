import os
from datetime import datetime
from threading import Thread

from get_cellar_ids import get_cellar_info_from_endpoint, get_cellar_ids_from_json_results, cellar_ids_to_file, get_cellar_ids_from_csv_file
from get_text_from_cellar_files import get_text
from get_cellar_docs import check_ids_to_download, process_range

from utils.file_utils import text_to_str, to_json_output_file

QUERY = 'queries/sparql_queries/financial_domain_sparql_2019-01-07.rq'
dir_to_check = "data/cellar_files_20240903-134646/"

# Set current time and date
timestamp = str(datetime.now().strftime("%Y%m%d-%H%M%S"))

# Specify folder path to store downloaded files
dwnld_folder_path = "data/cellar_files_" + timestamp + "/"

# Get SPARQL query from given file
sparql_query = text_to_str(QUERY)
print('SPARQL_PATH:', sparql_query)

# Get CELLAR information from EU SPARQL endpoint (in JSON format)
sparql_query_results = get_cellar_info_from_endpoint(sparql_query)

# Output SPARQL results to file
sparql_query_results_dir = "queries/sparql_query_results/"
os.makedirs(os.path.dirname(sparql_query_results_dir), exist_ok=True)
sparql_query_results_file = sparql_query_results_dir + "query_results_" + timestamp + ".json"
to_json_output_file(sparql_query_results_file, sparql_query_results)

# Create a list of ids from the SPARQL query results (in JSON format)
id_list = sorted(get_cellar_ids_from_json_results(sparql_query_results))
# print('ID_LIST:', len(id_list), id_list[:10])

# # ALTERNATIVELY
# # If you already have a CSV file with cellar ids,
# # e.g., copy-pasted from browser results,
# # specify file (path) containing the cellar IDs
# # Input format: cellarURIs,lang,mtypes,workTypes,subjects,subject_ids
# cellar_ids_file = 'queries/sparql_query_results/query_results_2019-01-07.csv'
# #
# # Create a list of CELLAR ids from the given CSV file
# id_list = get_cellar_ids_from_csv_file(cellar_ids_file)

# Output retrieved CELLAR ids list to txt file
# with each ID on a new line
cellar_ids_to_file(id_list, timestamp)


# Create a list of not-yet-downloaded file ids by comparing the results in id_list with files present in the given directory
if dir_to_check and os.path.exists(dir_to_check):
    id_list = check_ids_to_download(id_list, dir_to_check)
    print('NEW_FILES_TO_DOWNLOAD:', len(id_list))


# Run multiple threads in parallel to download the files
# using the process_range(sub_list, dwnld_folder_path) function
# Adapted from: https://stackoverflow.com/questions/16982569/making-multiple-api-calls-in-parallel-using-python-ipython
nthreads = 11
threads = []
for i in range(nthreads):  # Four times...
    # print('ID_LIST:', id_list[i::nthreads])
    sub_list = id_list[i::nthreads]
    t = Thread(target=process_range, args=(sub_list, dwnld_folder_path))
    threads.append(t)

# start the threads
[t.start() for t in threads]
# wait for the threads to finish
[t.join() for t in threads]


# Generate text files for downloaded XML and HTML files
# Set replace_existing to True to replace existing text files.
# To process only new files, set replace_existing to False (default).
# Usage: get_text(input_path, output_dir, replace_existing=False)
txt_folder_path = "data/text_files/text_" + dwnld_folder_path.split('_')[-1]
# print('TXT_DIR_PATH:', txt_folder_path)
get_text(dwnld_folder_path, txt_folder_path, replace_existing=False)
