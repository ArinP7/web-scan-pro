import requests, json, os
LOGIN  = "http://localhost:3000/rest/user/login"
LOGOUT = "http://localhost:3000/rest/user/logout"
ME     = "http://localhost:3000/rest/user/whoami"
s = requests.Session()
s.post(LOGIN, json={"email":"admin@juice-sh.op","password":"admin123"})
r1 = s.get(ME)
logged_in = r1.status_code == 200 and "email" in r1.json()
s.post(LOGOUT)
r2 = s.get(ME)
still_valid = r2.status_code == 200 and "email" in r2.json()
with open(os.path.join(os.getcwd(),"logout_invalid.json"),"w") as f:
    json.dump({"logged_in_before":logged_in,"session_still_valid_after_logout":still_valid},f,indent=2)
print("Still valid after logout?", still_valid)