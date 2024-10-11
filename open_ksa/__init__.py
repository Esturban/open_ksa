#__version__ = "0.1.0"  # Add this line with your desired version

from urllib.parse import urlparse, quote
from .download_file import download_file
from .get_dataset_resources import get_dataset_resources
from .get_org_resources import get_org_resources
from .ssl_adapter import SSLAdapter, SingletonSession
from .organizations import organizations