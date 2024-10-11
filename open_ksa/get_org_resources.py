import requests
from .ssl_adapter import SingletonSession
from urllib.parse import urlparse, quote

def get_org_resources(org_url = 'https://open.data.gov.sa/data/api/organizations',org_id = 'd69f01cd-ef1b-47e4-ad23-8e58a8d5a468'):
    session = SingletonSession.get_instance()
    
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://open.data.gov.sa/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #Parameters set for the organization - 
    #Here, we have defined this for the saudi port authority
    # To select a different organization, please visit the following website and copy the organization ID:  https://open.data.gov.sa/en/publishers
    # By finding the organization, visiting their page and copying the organization ID from the URL
    #
    params = {
        'version': '-1',
        'organization': org_id
    }

    # Make the request using the custom session
    response = session.get(org_url, params=params, headers=headers)
    
    try:
            data = response.json()
    except requests.exceptions.JSONDecodeError:
            print(f"Failed to decode JSON for dataset {org_id}")
    
    #print(data['nameEn'])
    return {'organization_name':data['nameEn'], 
            'organization_id':data['id'], 
            'dataset_ids':[dataset['id'] for dataset in data['datasets']]
            }
