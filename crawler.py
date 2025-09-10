#!/usr/bin/env python3
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
from helpers import normalize_url, is_same_domain


class SingleDomainCrawler:
    def __init__(self, base_url: str, max_pages=100, delay=1, session=None):
        self.base = normalize_url(base_url)
        self.max_pages = max_pages
        self.delay = delay
        self.session = session or requests.Session()
        self.session.headers.update(
            {"User-Agent": "single-domain-crawler/1.0 (+https://github.com/arinpodder)"}
        )

        self.visited = set()
        self.queue = [self.base]
        self.pages = {}
        self.forms = {}

    # ----------------------------------------------------
    def extract_links(self, html: str, page_url: str):
        soup = BeautifulSoup(html, "lxml")
        hrefs = []
        for a in soup.find_all("a", href=True):
            href = urljoin(page_url, a["href"])
            href = normalize_url(urldefrag(href)[0])
            if href:
                hrefs.append(href)
        return hrefs

    def extract_forms(self, html: str, page_url: str):
        soup = BeautifulSoup(html, "lxml")
        forms = []
        for form in soup.find_all("form"):
            action = urljoin(page_url, form.get("action") or "")
            method = (form.get("method") or "GET").upper()
            inputs = []
            for tag in form.find_all(["input", "textarea", "select", "button"]):
                inputs.append(
                    {
                        "type": tag.get("type", "text"),
                        "name": tag.get("name"),
                        "value": tag.get("value", ""),
                    }
                )
            forms.append({"method": method, "action": action, "inputs": inputs})
        return forms

    # ----------------------------------------------------
    def crawl(self):
        """Start the crawl and return collected data."""
        while self.queue and len(self.visited) < self.max_pages:
            url = self.queue.pop(0)
            url = normalize_url(url)
            if url in self.visited or not is_same_domain(self.base, url):
                continue

            try:
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
                html = resp.text
            except Exception as e:
                print(f"Skip {url} ({e})")
                self.visited.add(url)
                continue

            self.pages[url] = html
            forms_found = self.extract_forms(html, url)
            if forms_found:
                self.forms[url] = forms_found

            for link in self.extract_links(html, url):
                if link not in self.visited and link not in self.queue:
                    self.queue.append(link)

            self.visited.add(url)
            time.sleep(self.delay)

        return {"pages": self.pages, "forms": self.forms}


# ------------------------------------------------------------------
# Allow running as script, but **no self-import** so it can be imported too
if __name__ == "__main__":
    import argparse
    import json
    import pathlib
    import datetime

    parser = argparse.ArgumentParser(description="Single-domain web crawler")
    parser.add_argument("url", help="Base URL to start crawling")
    parser.add_argument("--max", type=int, default=50, help="Max pages to fetch")
    parser.add_argument("--delay", type=float, default=1.0, help="Politeness delay (s)")
    parser.add_argument("--out", default=".", help="Folder to save results")

    args = parser.parse_args()
    crawler = SingleDomainCrawler(args.url, max_pages=args.max, delay=args.delay)
    result = crawler.crawl()

    out = pathlib.Path(args.out)
    out.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    (out / f"pages_{stamp}.json").write_text(json.dumps(result["pages"], indent=2))
    (out / f"forms_{stamp}.json").write_text(json.dumps(result["forms"], indent=2))
    print(f"Crawled {len(result['pages'])} pages, saved to {out}")