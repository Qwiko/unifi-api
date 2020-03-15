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
        self._login_data['remember'] = True
        self._site = site
        self._verify_ssl = verify_ssl
        self._baseurl = baseurl
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
        #print("logging in")
        try:
            self._current_status_code = self._session.post("{}/api/login".format(self._baseurl), data=json.dumps(self._login_data), verify=self._verify_ssl).status_code
            if self._current_status_code == 200:
                self.connected = True
                #print("Logged in")
            if self._current_status_code == 400:
                self.connected = False
                raise LoggedInException("Failed to log in to api with provided credentials")
        except requests.exceptions.ConnectionError:
            self.connected = False
            #print("Failed to login")


    def logout(self):
        """
        Log the user out

        :return: None
        """
        self._session.get("{}/logout".format(self._baseurl))
        self._session.close()


    def get_guest_password(self):
        #Get request
        #api/s/{site}/rest/setting

        r = self._session.get("{}/api/s/{}/get/setting/guest_access".format(self._baseurl, self._site, verify=self._verify_ssl), data="json={}")
        #print(r.json())
        data = r.json()['data']
        #print(data)
        try:
            password = data[0]["x_password"]
        except IndexError:
            print("IndexError, logging in again")
            self.login()
        return {"password": password}

    def set_guest_password(self, password = None):
        if not password:
            #Get new password
            response = requests.get('https://passwordwolf.com/api/?upper=off&special=off&length=8&exclude=%3F!%3C%3Eli1I0OB8%60&repeat=1')
            password = response.json()[0]["password"]

        data = {}
        data["x_password"] = password
        
        url = self._baseurl + "/api/s/" + self._site + "/rest/setting/guest_access/"

        r = self._session.put("{}".format(url, verify=self._verify_ssl), data=json.dumps(data))
        
        if r.status_code == 200:
            newPW = r.json()["data"][0]["x_password"]
            return {"password": newPW}
        else:
            print("Error trying to login again")
            self.login()
            return "error"
    
    def list_clients(self, filters: Dict[str, Union[str, Pattern]]=None, order_by: str=None) -> list:
        """
        List all available clients from the api

        :param filters: dict with valid key, value pairs, string supplied is compiled to a regular expression
        :param order_by: order by a valid client key, defaults to '_id' if key is not found
        :return: A list of clients on the format of a dict
        """

        r = self._session.get("{}/api/s/{}/stat/sta".format(self._baseurl, self._site, verify=self._verify_ssl), data="json={}")
        self._current_status_code = r.status_code
        
        if self._current_status_code == 401:
            raise LoggedInException("Invalid login, or login has expired")

        data = r.json()['data']

        if filters:
            for term, value in filters.items():
                value_re = value if isinstance(value, Pattern) else re.compile(value)

                data = [x for x in data if term in x.keys() and re.fullmatch(value_re, x[term])]

        if order_by:
            data = sorted(data, key=lambda x: x[order_by] if order_by in x.keys() else x['_id'])

        return data
