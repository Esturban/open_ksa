from urllib.parse import urlparse, quote
from .download_file import download_file
from .ssl_adapter import SingletonSession
import requests
import os
import time

def get_dataset_resource(dataset_id,allowed_exts=['csv', 'xlsx', 'xls'], output_dir=f"opendata/org_resources", headers = None, verbose = None):
    """For each dataset, download the available resources that meet the extensions criteria

    Args:
        dataset_id (str): The dataset ID to download resources from
        allowed_exts (list, optional): The list of allowed file extensions to try to download. Defaults to ['csv', 'xlsx', 'xls'].
        output_dir (str, optional): The directory to save the downloaded files. Defaults to f"opendata/org_resources".
        headers (list, optional): The list of headers to use for the request. Defaults to None.
        verbose (bool, optional): Whether to print verbose output. Defaults to None.

    Returns:
        None: No value returned
    """
    #Assign the default headers to get the correesponding resources
    if headers is None:
        headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://open.data.gov.sa/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host':'open.data.gov.sa',
        'Upgrade-Insecure-Requests':'1'
        }
    #Create the session item for the requests instance
    session = SingletonSession.get_instance()
    dataset_params = {
            'version': '-1',
            'dataset': dataset_id
        }
    dataset_response = session.get('https://open.data.gov.sa/data/api/datasets/resources', params=dataset_params, headers=headers)

    # Check if the response contains valid JSON
    try:
        dataset_data = dataset_response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to decode JSON for dataset {dataset_id}")
        return None

    for resource in dataset_data['resources']:
            download_url = resource['downloadUrl']
            parsed_url = urlparse(download_url)
            file_extension = os.path.splitext(parsed_url.path)[1][1:]  # Get the file extension without the dot
            
            # Skip the file if its extension is not in the allowed list
            if file_extension not in allowed_exts:
                if(verbose):print(f"Skipping file with extension {file_extension}: {download_url}")
                continue
            
            #URLs to try
            safe_url = parsed_url._replace(path=quote(parsed_url.path, safe='/')).geturl()
            lr_url = f'https://open.data.gov.sa/data/api/v1/datasets/{dataset_data['datasetId']}/resources/{resource['id']}/download'

            # Construct the output file path
            file_name = os.path.basename(parsed_url.path)
            resource_file_path = os.path.join(output_dir, file_name)
            
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Check if the file already exists and its size
            if os.path.exists(resource_file_path) and os.path.getsize(resource_file_path) > 250:
                if(verbose):print(f"Skipping existing file: {resource_file_path}")
                continue

            # Check if the file already exists, its size, and its age
            if os.path.exists(resource_file_path):
                file_age = time.time() - os.path.getmtime(resource_file_path)
                if os.path.getsize(resource_file_path) > 250 and file_age <= 7 * 24 * 60 * 60:
                    if(verbose):print(f"Skipping existing file: {resource_file_path}")
                    continue
                elif file_age > 7 * 24 * 60 * 60:
                    if(verbose):print(f"Deleting old file: {resource_file_path}")
                    os.remove(resource_file_path)

            # Add headers to mimic a browser request
            download_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': f'https://open.data.gov.sa/en/datasets/view/{dataset_data['datasetId']}/resources',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Host':'open.data.gov.sa',
                'Upgrade-Insecure-Requests':'1', 
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive'
            }
            
            if(verbose):
                print(f"OG URL: {download_url}")
                print(f"SA URL: {safe_url}")
            
            # Attempt to download using the safe URL
            file_size = download_file(session,lr_url, download_headers, resource_file_path)
            
            # If the file is less than 250 bytes, attempt to download using the original URL
            if file_size <= 250:
                if(verbose):print(f"File {file_name} is less than 250 bytes, retrying with original URL")
                file_size = download_file(session,safe_url, download_headers, resource_file_path)
            
            if file_size > 250:
                if(verbose):print(f"Downloaded and saved file: {resource_file_path}")
            else:
                if(verbose):print(f"Failed to download a valid file for: {file_name}")

