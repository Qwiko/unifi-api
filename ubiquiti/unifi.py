from requests import Session
import requests
import json
import re
import time
from typing import Pattern, Dict, Union
import urllib3
urllib3.disable_warnings()

class LoggedInException(Exception):

    def __init__(self, *args, **kwargs):
        super(LoggedInException, self).__init__(*args, **kwargs)


class API(object):
    """
    Unifi API for the Unifi Controller.

    """
    _login_data = {}
    _current_status_code = None

    def __init__(self, username: str="ubnt", password: str="ubnt", site: str="default", baseurl: str="https://unifi:8443", verify_ssl: bool=True):
        """
        Initiates tha api with default settings if none other are set.

        :param username: username for the controller user
        :param password: password for the controller user
        :param site: which site to connect to (Not the name you've given the site, but the url-defined name)
        :param baseurl: where the controller is located
        :param verify_ssl: Check if certificate is valid or not, throws warning if set to False
        """
        self._login_data['username'] = username
        self._login_data['password'] = password
        self._login_data['rememberMe'] = True
        self._site = site
        self._verify_ssl = verify_ssl
        self._baseurl = baseurl
        #print(username)
        self._session = Session()
        # print(self.__dict__)
        # print(self._login_data)

    def __enter__(self):
        """
        Contextmanager entry handle

        :return: isntance object of class
        """
        self.login()
        return self

    def __exit__(self, *args):
        """
        Contextmanager exit handle

        :return: None
        """
        self.logout()

    def login(self):
        """
        Log the user in

        :return: None
        """

        try:
            response = self._session.post("{}/api/auth/login".format(self._baseurl), json=self._login_data, verify=self._verify_ssl)
            self._current_status_code = response.status_code
            self.setHeaders(response)
            #self._session.headers["x-csrf-token"] = response.headers["x-csrf-token"]
            if self._current_status_code == 200:
                self.connected = True
            if self._current_status_code == 400:
                self.connected = False
                raise LoggedInException("Failed to log in to api with provided credentials")
            if self._current_status_code == 401:
                self.connected = False
                raise LoggedInException("Invalid username or password")
        except requests.exceptions.ConnectionError:
            self.connected = False

        #Set headers
        self._session.headers["Content-Type"] = "application/json"
        self._session.headers["Connection"] = "keep-alive"




    def _send(self, endpoint, json={}, method="GET"):
        url = self._baseurl + "/proxy/network/api/s/" + self._site + endpoint

        #Passing in data switch to POST-request
        if json:
            method = "POST"
        
        self._session.headers["content-length"] = str(len(json))
        
        response = self._session.request(method, url, verify=self._verify_ssl, json=json)
        self.setHeaders(response)
        return response

    def logout(self):
        """
        Log the user out

        :return: None
        """
        self._session.get("{}/api/auth/logout".format(self._baseurl))
        self._session.close()


    def setHeaders(self, response):
        #print(headers)
        csrf_token =  response.headers.get("x-csrf-token")
        if csrf_token:
            self._session.headers["x-csrf-token"] = csrf_token


    def get_guest_password(self):
        #Get request
        r = self._send("/rest/setting/guest_access/")

        password = "error"
        try:
            data = r.json()['data']
            password = data[0]["x_password"]
        except IndexError:
            print("IndexError, logging in again")
            self.login()
        
        except json.decoder.JSONDecodeError:
            print("JSON decoder error")
            print("Content:")
            print(r.content)
            print()
            return {"error": "JSON decoder error"}, 404
        return {"password": password}

    def set_guest_password(self, password = None):
        r = self._send("/rest/setting/guest_access/")

        data = r.json()['data']
        guest_access_id = data[0]["_id"]
        current_password = data[0]["x_password"]
        

        if current_password == password:
            return {"error": "Password is already set"}, 406

        if not password:
            #Get new password
            response = requests.get('https://passwordwolf.com/api/?upper=off&special=off&length=8&exclude=%3F!%3C%3Eli1I0OB8%60&repeat=1')
            password = response.json()[0]["password"]
        

        r = self._send("/set/setting/guest_access/" + guest_access_id, {"x_password": password})

        if r.status_code == 200:
            newPW = r.json()["data"][0]["x_password"]
            return {"password": newPW}
        else:
            print("Error trying to login again")
            self.login()
            return "error"