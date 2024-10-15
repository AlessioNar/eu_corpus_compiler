#!/usr/bin/python
# coding=<utf-8>

"""
Program to get the text from the XML and HTML files
downloaded from the EU CELLAR server, clean it up,
and print it to a new text file.

If replace_existing=False (default setting),
the program checks the output_dir
for existing text files and only processes files
from which the text has not yet been extracted.

Usage: get_text(input_path, output_dir, replace_existing=False)

The input_path can be a dir name ending with "/"
or a text file containing a list of file names.
The output_dir name must also end with "/".

XML files with ".doc." and ".toc." in their names are excluded
as they only contain metadata.

Note that:
- Footnotes in XML files are currently deleted to avoid them being inserted in the middle of a sentence.
- The text from nested tables in HTML files is repeated.
"""

import os
import sys
from tqdm import tqdm
from utils.file_utils import get_file_list_from_path
from utils.html2txt import html2txt_path_eu
from utils.xml2txt import xml2txt_bs4_eu

sys.path.append("..")

def get_input_files(input_path):
    """
    Get the list of input files based on the input_path.
    
    Args:
    input_path (str): The path to the input directory or file.
    
    Returns:
    list: A list of file paths.
    """
    if input_path.endswith('/'):
        xml_files = get_file_list_from_path(input_path, name='', extension='.xml')
        html_files = get_file_list_from_path(input_path, name='', extension='.html')
        return xml_files + html_files
    else:
        with open(input_path, 'r') as file:
            return [line.strip() for line in file.readlines()]

def get_existing_output_files(output_dir):
    """
    Get the list of existing output files in the output directory.
    
    Args:
    output_dir (str): The path to the output directory.
    
    Returns:
    list: A list of existing output file names without extension.
    """
    existing_files = get_file_list_from_path(output_dir, name='', extension='.txt')
    return [os.path.basename(file).replace('.txt', '') for file in existing_files]

def process_file(file_path, output_dir, replace_existing):
    """
    Process a single file and write the extracted text to the output directory.
    
    Args:
    file_path (str): The path to the file to process.
    output_dir (str): The path to the output directory.
    replace_existing (bool): Whether to replace existing output files.
    """
    file_name = os.path.basename(file_path).replace('.html', '').strip()
    cellar_id = os.path.basename(os.path.dirname(file_path))

    if not replace_existing and file_name in get_existing_output_files(output_dir):
        return

    if file_path.endswith('.html'):
        text = html2txt_path_eu(file_path)
        print(f'Processing file: <HTML> {cellar_id}/{file_name}')
    elif file_path.endswith('.xml') and '.doc.' not in file_path and '.toc.' not in file_path:
         text = xml2txt_bs4_eu(file_path)
         print(f'Processing file: <XML> {cellar_id}/{file_name}')
    
    else:
        return

    if text:
        output_file_path = os.path.join(output_dir, f'{file_name}.txt')
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'w+', encoding="utf-8") as file:
            file.write(text)

def get_text(input_path, output_dir, replace_existing=False):
    """
    Get the text from the XML and HTML files
    downloaded from the EU CELLAR server, clean it up,
    and print it to a new text file.
    
    Args:
    input_path (str): The path to the input directory or file.
    output_dir (str): The path to the output directory.
    replace_existing (bool): Whether to replace existing output files.
    """
    input_files = get_input_files(input_path)
    pbar = tqdm(total=len(input_files), desc='Processing files')

    for file_path in input_files:
        process_file(file_path, output_dir, replace_existing)
        pbar.update(1)

if __name__ == '__main__':
    input_path = '/path/to/input/directory/'
    output_dir = '/path/to/output/directory/'
    get_text(input_path, output_dir, replace_existing=True)