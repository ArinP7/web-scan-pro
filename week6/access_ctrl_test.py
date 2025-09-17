# access_ctrl_test.py
import requests, json, datetime, os

LOGIN = "http://localhost:3000/rest/user/login"
ADMIN = "http://localhost:3000/rest/admin/application-version"

# 1. login as normal user
s = requests.Session()
s.post(LOGIN, json={"email": "jim@juice-sh.op", "password": "ncc-1701"})

# 2. try admin endpoint
r = s.get(ADMIN)
access = r.status_code == 200 and "version" in r.text

out = {"admin_endpoint_accessible": access, "timestamp": str(datetime.datetime.now())}
with open(os.path.join(os.getcwd(), "access_ctrl_test.json"), "w") as f:
    json.dump(out, f, indent=2)
print("Admin access?", access)