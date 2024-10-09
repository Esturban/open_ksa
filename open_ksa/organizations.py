import requests
import json
import csv
import os

def organizations(headers=None, size=400, page=0, sort='datasetsCount,DESC', target=None):
    """Fetch organizations from the API and save to a file if target is specified.

    Args:
        header (dict, optional): The header to use for the request of the API call. Defaults to None.
        size (int, optional): The size of the response. Defaults to 400.
        page (int, optional): The page number. Defaults to 0.
        sort (str, optional): The sort order. Defaults to 'datasetsCount,DESC'.
        target (str, optional): The file path to save the data. Defaults to None.

    Returns:
        dict: The response from the API call for the organization.
    """
    if headers is None:
        
        headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://open.data.gov.sa/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host':'open.data.gov.sa',
        'Upgrade-Insecure-Requests':'1'
        }

    params = {'size': size, 'page': page, 'sort': sort}


    response = requests.get('https://open.data.gov.sa/api/organizations', params=params,headers=headers)
    print(response)
    if response.status_code == 200:
        try:
            # Try to parse JSON response
            data = response.json()
            if target is not None:
                # Check if target is a complete filepath
                if not os.path.isabs(target):
                    target = os.path.join(os.getcwd(), target)
                
                _, file_extension = os.path.splitext(target)
                if file_extension.lower() == '.json':
                    # Write data to JSON file
                    with open(target, 'w') as jsonfile:
                        json.dump(data, jsonfile, indent=4)
                    return data
                elif file_extension.lower() == '.csv':
                    # Write data to CSV file
                    with open(target, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        # Write headers
                        writer.writerow(data['content'][0].keys())
                        # Write data rows
                        for item in data['content']:
                            writer.writerow(item.values())
            else:
                # Print the first 10 values in the terminal
                for item in data['content'][:10]:
                    print(item)
                return data
            return data
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode JSON. Here is the raw response:")
            print(response.text)
            # Print the raw response if JSON decoding fails
