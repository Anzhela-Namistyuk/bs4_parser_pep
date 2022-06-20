from pathlib import Path
from urllib.parse import urljoin

MAIN_DOC_URL_PEP = 'https://peps.python.org/'

MAIN_DOC_URL = 'https://docs.python.org/3/'
whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}
