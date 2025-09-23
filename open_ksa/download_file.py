import os
import json
import requests


def download_file(
    session, url, headers, file_path, resource_id=None, verbose=None, skip_blank=True
):
    """Download the corresponding file from the Open Data Portal

    Args:
        session (Session): The session object to use for the request
        url (str): The download URL for the file to try and download it locally
        headers (dict): The dictionary of headers to be used in the GET request
        file_path (str): Absolute path of where to download the file
        resource_id (str): The ID of the resource
        skip_blank (bool): Whether to skip downloading blank files (default: True)

    Returns:
        int: The length of the downloaded file in bytes
    """
    missing_file_path = os.path.join(os.path.dirname(file_path), "missing.json")

    # Load existing missing IDs
    if os.path.exists(missing_file_path):
        with open(missing_file_path, "r") as f:
            missing_ids = set(json.load(f))
    else:
        missing_ids = set()

    # Remove resource_id to retry downloading
    missing_ids.discard(resource_id)

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()

        # Decode content based on the response's encoding
        content = response.content.decode(response.encoding or "utf-8", errors="ignore")
        if (
            content == "NO DATA FOUND"
            or content.startswith("<html>")
            or not content.strip()
        ):
            if verbose:
                print(f"Invalid content received from {url}")
            # Mark resource as missing
            missing_ids.add(resource_id)
            with open(missing_file_path, "w") as f:
                json.dump(list(missing_ids), f, indent=4)
            if skip_blank:
                return 0

        else:
            # Write the content to the file
            with open(file_path, "wb") as file:
                file.write(response.content)
            # Ensure resource_id is not marked as missing
            missing_ids.discard(resource_id)
            with open(missing_file_path, "w") as f:
                json.dump(list(missing_ids), f, indent=4)
            return len(response.content)
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"Failed to download {url}: {e}")
        # Mark resource as missing on exception
        missing_ids.add(resource_id)
        with open(missing_file_path, "w") as f:
            json.dump(list(missing_ids), f, indent=4)
        return 0
