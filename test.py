import json,  time
from requests import Session, request
import requests
from ubiquiti.unifi import API as Unifi_API
config = json.load(open('config.json','r'))
#config.baseurl = "https://localhost:8443"

UniFi_api = Unifi_API(username=config["username"], password=config["password"], baseurl=config["baseurl"], site=config["site"], verify_ssl=config["verify_ssl"])
UniFi_api.login()




#print(UniFi_api.get_guest_password())
# print(UniFi_api.get_guest_password())
# print(UniFi_api.get_guest_password())
# print(UniFi_api.get_guest_password())

print(UniFi_api.set_guest_password("testtest"))

# session = UniFi_api._session

# r = session.get("{}/api/s/{}/get/setting/guest_access".format(UniFi_api._baseurl, UniFi_api._site, verify=UniFi_api._verify_ssl), data="json={}")

# print(r.content)


#print(session.__dict__)
# session = Session()
# baseurl = "https://unifi.mgmt/network:8443"
# site = "bqb9c22w"
# verify_ssl = False
# login_data = {"username": "api", "password": "apitest"}
# payload = "{\"username\": \"api\",\r\n\"password\": \"apitest\", \"remember\":true}"




# res = request("POST", baseurl + "/api/login".format(baseurl), data=payload, verify=verify_ssl)

# print(res.status_code)
# print(res.content)


