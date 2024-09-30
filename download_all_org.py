# -*- coding: utf-8 -*-
#
# Downloading all of the datasets of a single organization ID, if applicable from the opendata portal from KSA
#
# First, an SSL adapter is made to handle https requests
# Headers are set to mimic a browser
# An organization's full list of resources is retrieved
# Then, we go through all resources to collect the downloadURL links
# Once all downloadURL's are collected, an array is made and a loop goes through each download URL
# Downloads all of the files to a folder called 'opendata/{organizationid}'
# Not, some datasets are still broken, but some decent coverage
#
#

import os
import requests
import ssl
from src import get_org_resources, get_dataset_resources
import time
from urllib3 import poolmanager
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, quote

# Custom adapter to allow unsafe SSL legacy renegotiation
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

# Create a session and mount the custom SSL adapter
session = requests.Session()
session.mount('https://', SSLAdapter())

#Parameters for running the script
allowed_exts = ['csv','xlsx','xls']
verbose = False


# Extract the organization ID and dataset IDs
resources =get_org_resources.get_org_resources(session=session,org_id = '3910a763-1829-445f-97b1-2bd988249b7e')
dataset_ids = resources['dataset_ids']
organization_id= resources['organization_id']

# Create a directory named after the organization ID
output_dir = f"opendata/{resources['organization_name'].strip().replace(' ','_').lower()}"
os.makedirs(output_dir, exist_ok=True)

#Get all of the data resources for the organization
get_dataset_resources.get_dataset_resources(dataset_ids = dataset_ids,session = session,allowed_exts = allowed_exts,output_dir = output_dir,verbose = verbose)
