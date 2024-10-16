
import os
import requests

import time

from .download_file import download_file
from .get_dataset_resource import get_dataset_resource
from urllib.parse import urlparse, quote
from .ssl_adapter import SingletonSession


def get_dataset_resources(dataset_ids,allowed_exts=['csv', 'xlsx', 'xls'],output_dir=f"opendata/org_resources",verbose = False):
    """Download the resources for each dataset in the list of dataset IDs

    Args:
        dataset_ids (list): The list of dataset IDs to download resources from
        allowed_exts (list, optional): The list of allowed file extensions to try to download. Defaults to ['csv', 'xlsx', 'xls'].
        output_dir (str, optional): The directory to save the downloaded files. Defaults to f"opendata/org_resources".
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    """
    session = SingletonSession.get_instance()
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://open.data.gov.sa/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Download each dataset and save it to the directory
    for dataset_id in dataset_ids: get_dataset_resource(dataset_id,allowed_exts,output_dir,headers,verbose)
        