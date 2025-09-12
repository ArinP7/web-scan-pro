import sys, json
from crawler import SingleDomainCrawler

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    max_p = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    c = SingleDomainCrawler(base, max_pages=max_p, delay=0.5)
    res = c.crawl()
    print(json.dumps(res["forms"], indent=2)[:1000] + "...")