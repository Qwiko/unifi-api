import json, config, time
from ubiquiti.unifi import API as Unifi_API

config.baseurl = "https://localhost:8443"

UniFi_api = Unifi_API(username=config.username, password=config.password, baseurl=config.baseurl, site=config.site, verify_ssl=config.verify_ssl)
#UniFi_api.login()


def getStatus():
    UniFi_api.login()
    if not UniFi_api.connected:
        status = "Disconnected"
    elif UniFi_api.connected:
        status = "Connected"
    return {"status": status}


print(getStatus())