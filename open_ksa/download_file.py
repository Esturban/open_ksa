# Function to download a file
import requests

def download_file(session, url, headers, file_path):
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return len(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return 0
