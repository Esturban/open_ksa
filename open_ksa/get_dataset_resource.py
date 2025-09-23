from urllib.parse import urlparse, quote
from .download_file import download_file
from .ssl_adapter import SingletonSession
import requests
import os
import time


def get_dataset_resource(
    dataset_id,
    allowed_exts=["csv", "xlsx", "xls"],
    output_dir=f"opendata/org_resources",
    ext_dir=None,
    headers=None,
    verbose=None,
):
    """For each dataset, download the available resources that meet the extensions criteria

    Args:
        dataset_id (str): The dataset ID to download resources from
        allowed_exts (list, optional): The list of allowed file extensions to try to download. Defaults to ['csv', 'xlsx', 'xls'].
        output_dir (str, optional): The directory to save the downloaded files. Defaults to f"opendata/org_resources".
        headers (list, optional): The list of headers to use for the request. Defaults to None.
        ext_dir (bool, optional): The directory to save the downloaded files. Defaults to None.
        verbose (bool, optional): Whether to print verbose output. Defaults to None.

    Returns:
        None: No value returned
    """
    # Assign the default headers to get the correesponding resources
    if headers is None:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://open.data.gov.sa/",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "open.data.gov.sa",
            "Upgrade-Insecure-Requests": "1",
        }
    # Create the session item for the requests instance
    session = SingletonSession.get_instance()
    dataset_params = {"version": "-1", "dataset": dataset_id}
    dataset_response = session.get(
        "https://open.data.gov.sa/data/api/datasets/resources",
        params=dataset_params,
        headers=headers,
    )

    # Check if the response contains valid JSON
    try:
        dataset_data = dataset_response.json()
    except requests.exceptions.JSONDecodeError:
        if verbose:
            print(f"Failed to decode JSON for dataset {dataset_id}")
        return None
    parent_dir = output_dir

    # Initialize statistics for this dataset
    stats = {
        "total": 0,
        "checked": 0,
        "failed": 0,
        "skipped": 0,  # Initialize skipped count
        "downloaded": 0,
        "extensions": allowed_exts,
    }

    for resource in dataset_data["resources"]:
        stats["total"] += 1
        if verbose:
            print(f"Attempting to download resource: {resource['downloadUrl']}")
        download_url = resource["downloadUrl"]
        parsed_url = urlparse(download_url)
        # Extract the file extension
        file_name = os.path.basename(parsed_url.path)
        file_extension = os.path.splitext(file_name)[1].lstrip(".")

        # Skip the file if its extension is not in the allowed list
        if file_extension not in allowed_exts:
            if verbose:
                print(f"Skipping file with extension {file_extension}: {download_url}")
            stats["skipped"] += 1
            continue
        stats["checked"] += 1
        # URLs to try
        safe_url = parsed_url._replace(path=quote(parsed_url.path, safe="/")).geturl()
        lr_url = f"https://open.data.gov.sa/data/api/v1/datasets/{dataset_data['datasetId']}/resources/{resource['id']}/download"

        # Construct the output file path
        output_dir = (
            parent_dir if ext_dir is None else os.path.join(parent_dir, file_extension)
        )
        resource_file_path = os.path.join(output_dir, file_name)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Check if the file already exists and its size
        if (
            os.path.exists(resource_file_path)
            and os.path.getsize(resource_file_path) > 250
        ):
            if verbose:
                print(f"Skipping existing file: {resource_file_path}")
            stats["downloaded"] += 1
            continue

        # Check if the file already exists, its size, and its age
        if os.path.exists(resource_file_path):
            file_age = time.time() - os.path.getmtime(resource_file_path)
            if (
                os.path.getsize(resource_file_path) > 250
                and file_age <= 7 * 24 * 60 * 60
            ):
                if verbose:
                    print(f"Skipping existing file: {resource_file_path}")
                stats["downloaded"] += 1
                continue
            elif file_age > 7 * 24 * 60 * 60:
                if verbose:
                    print(f"Deleting old file: {resource_file_path}")
                os.remove(resource_file_path)

        # Add headers to mimic a browser request for the dataset resource download endpoint
        download_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": f"https://open.data.gov.sa/en/datasets/view/{dataset_data['datasetId']}/resources",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "open.data.gov.sa",
            "Upgrade-Insecure-Requests": "1",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        }

        if verbose:
            print(f"OG URL: {download_url}")
            print(f"SA URL: {safe_url}")

        # Attempt to download using the dataset resource download endpoint first (lr_url)
        file_size = download_file(session, lr_url, download_headers, resource_file_path)

        # If lr_url did not return a valid file, fall back to the original (safe) URL
        if file_size == 0:
            if verbose:
                print(
                    f"lr_url did not return valid content; retrying with original URL {safe_url}"
                )
            fallback_headers = {
                "User-Agent": download_headers["User-Agent"],
                "Referer": "https://open.data.gov.sa/",
                "Accept-Language": "en-US,en;q=0.9",
            }
            file_size = download_file(
                session, safe_url, fallback_headers, resource_file_path
            )

        if file_size > 250:
            if verbose:
                print(f"Downloaded and saved file: {resource_file_path}")
            stats["downloaded"] += 1
        else:
            if verbose:
                print(f"Failed to download a valid file for: {file_name}")
            stats["failed"] += 1

    return stats
