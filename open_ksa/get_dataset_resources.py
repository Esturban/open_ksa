
import os
import requests

import time

from .download_file import download_file
from urllib.parse import urlparse, quote
from .ssl_adapter import SingletonSession


def get_dataset_resources(dataset_ids,allowed_exts=['csv', 'xlsx', 'xls'],output_dir=f"opendata/org_resources",verbose = False):
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
    for dataset_id in dataset_ids:
        
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
            continue

        #print(dataset_data)
        # Iterate over each resource in the dataset
        for resource in dataset_data['resources']:
            download_url = resource['downloadUrl']
            parsed_url = urlparse(download_url)
            file_extension = os.path.splitext(parsed_url.path)[1][1:]  # Get the file extension without the dot
            
            # Skip the file if its extension is not in the allowed list
            if file_extension not in allowed_exts:
                if(verbose):print(f"Skipping file with extension {file_extension}: {download_url}")
                continue
            
            safe_url = parsed_url._replace(path=quote(parsed_url.path, safe='/')).geturl()
            file_name = os.path.basename(parsed_url.path)
            resource_file_path = os.path.join(output_dir, file_name)
            
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
                'Referer': 'https://open.data.gov.sa/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            if(verbose):
                print(f"OG URL: {download_url}")
                print(f"SA URL: {safe_url}")
            
            # Attempt to download using the safe URL
            file_size = download_file(session,safe_url, download_headers, resource_file_path)
            
            # If the file is less than 250 bytes, attempt to download using the original URL
            if file_size <= 250:
                if(verbose):print(f"File {file_name} is less than 250 bytes, retrying with original URL")
                file_size = download_file(session,download_url, download_headers, resource_file_path)
            
            if file_size > 250:
                if(verbose):print(f"Downloaded and saved file: {resource_file_path}")
            else:
                if(verbose):print(f"Failed to download a valid file for: {file_name}")