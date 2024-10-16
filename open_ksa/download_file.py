# Function to download a file
import requests

def download_file(session, url, headers, file_path,verbose = None,skip_blank = True):
    """Download the corresponding file from the Open Data Portal

    Args:
        session (Session): The session object to use for the request
        url (str): The download URL for the file to try and download it locally
        headers (list): The list of headers to be used in the GET request
        file_path (str): Absolute path of where to download the file
        skip_blank (bool): Whether to skip downloading blank files (default: True)

    Returns:
        int: The length of the downloaded file in bytes
    """
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        

        content = response.content.decode('utf-8', errors='ignore')
        if content == "NO DATA FOUND" or content.startswith("<html>"):
            if verbose: print(f"Invalid content received from {url}")
            if skip_blank: return 0
        
        # Write the content to the file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        return len(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return 0