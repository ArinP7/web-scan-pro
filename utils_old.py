# utils.py
import requests, re
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "sqlmap-lite/0.1"}

def get_session():
    """Return a requests Session with sane defaults."""
    sess = requests.Session()
    sess.headers.update(HEADERS)
    return sess

# Common SQL error fingerprints
_ERROR_REGEXES = [
    re.compile(r"SQL syntax.*?MySQL"),
    re.compile(r"Warning.*?\Wmysqli?_"),
    re.compile(r"PostgreSQL.*?ERROR"),
    re.compile(r"Microsoft OLE DB.*?error"),
    re.compile(r"ORA-\d{5}"),
]

def find_sql_errors(text: str):
    """Return (found: bool, pattern: str) if the page shows SQL errors."""
    for pat in _ERROR_REGEXES:
        if pat.search(text):
            return True, pat.pattern
    return False, None