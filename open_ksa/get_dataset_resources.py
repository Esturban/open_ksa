
import os
import requests
import concurrent.futures
import time

from .download_file import download_file
from .get_dataset_resource import get_dataset_resource
from urllib.parse import urlparse, quote
from .ssl_adapter import SingletonSession


def get_dataset_resources(dataset_ids,allowed_exts=['csv', 'xlsx', 'xls'],output_dir=f"opendata/org_resources",verbose = None, ext_dir=None, max_workers=None):
    """Download the resources for each dataset in the list of dataset IDs

    Args:
        dataset_ids (list): The list of dataset IDs to download resources from
        allowed_exts (list, optional): The list of allowed file extensions to try to download. Defaults to ['csv', 'xlsx', 'xls'].
        output_dir (str, optional): The directory to save the downloaded files. Defaults to f"opendata/org_resources".
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
        ext_dir (bool, optional): The directory to save the downloaded files. Defaults to None.
        max_workers (int, optional): The maximum number of workers to use for the concurrent download. Defaults to None.

    Returns:
        None: No value returned. Files downloaded to specified directory in `output_dir`
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
        # Function to download a single dataset resource
    def download_resource(dataset_id):
        get_dataset_resource(dataset_id=dataset_id, allowed_exts=allowed_exts, output_dir=output_dir, headers=headers, ext_dir=ext_dir, verbose=verbose)

    # Download each dataset and save it to the directory

    if max_workers:
         with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(download_resource, dataset_ids)
    else:
        for dataset_id in dataset_ids: download_resource(dataset_id = dataset_id)
        