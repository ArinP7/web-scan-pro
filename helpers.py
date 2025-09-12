import re
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
import tldextract

def normalize_url(url: str) -> str:
    """Lower-case scheme+netloc, strip fragments, sort query params, remove trailing /."""
    if not url:
        return ""
    scheme, netloc, path, query, fragment = urlsplit(url.strip())
    scheme = scheme.lower()
    netloc = netloc.lower()
    path = path or "/"
    if path.endswith("/") and len(path) > 1:
        path = path.rstrip("/")
    query = urlencode(sorted(parse_qsl(query)))
    return urlunsplit((scheme, netloc, path, query, ""))

def is_same_domain(base: str, url: str) -> bool:
    """True if registered domain (e.g. example.co.uk) is identical."""
    base_host = tldextract.extract(base).registered_domain
    url_host  = tldextract.extract(url).registered_domain
    return base_host == url_host and bool(base_host)

# You can later drop in extract_links & extract_forms here if you want to
# avoid importing BeautifulSoup inside crawler.py