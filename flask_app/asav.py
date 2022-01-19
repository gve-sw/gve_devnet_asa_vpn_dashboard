#!/usr/bin/env python3
'''
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''
import requests
import base64
import sys, json
import pprint

requests.packages.urllib3.disable_warnings()

class ASAVcontroller (object):

    def __init__(self, url, username, password):

        """Return ASAv object whose attributes are host, username and password.
        init
        """
        self.url = "https://" + url
        self.username = username
        self.password = password

        self.credentials = base64.encodebytes(bytes(self.username+ ":" + self.password, "utf-8")).decode("utf-8")


    def makeCall(self, p_url, method, data=""):

        headers={}
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = "REST API Agent"
        headers["Authorization"] = "Basic " + self.credentials[:len(self.credentials) -1]

        if method == "POST":
            response = requests.post(self.url + p_url, data=data, headers=headers, verify=False)
        elif method == "GET":
            response = requests.get(self.url + p_url, headers=headers, verify=False)
        elif method == "DELETE":
            response = requests.delete(self.url + p_url, headers=headers, verify=False)

        pprint.pprint(json.loads(response.text))
        if 199 < response.status_code < 300:
            return response
        else:
            error_message = json.loads(response.text)
            raise Exception(error_message)

    def showVPN(self):
        api_url = "/api/cli"
        data = {
            "commands": [
            "show vpn-sessiondb anyconnect"
            ]
        }

        pprint.pprint(json.dumps(data))
        self.makeCall(
            p_url = api_url,
            data=json.dumps(data),
            method="POST"
        )

    def showVPNDetail(self):
        api_url = "/api/cli"
        data = {
            "commands": [
                "show vpn-sessiondb detail anyconnect"
            ]
        }

        pprint.pprint(json.dumps(data))
        response = self.makeCall(
            p_url=api_url,
            data=json.dumps(data),
            method="POST"
        )

        response = json.loads(response.text)
        vpn_detail = response["response"]

        return vpn_detail


    def showLoadBalancing(self):
        api_url = "/api/cli"
        data = {
            "commands": [
                "show vpn load-balancing"
            ]
        }

        pprint.pprint(json.dumps(data))
        response = self.makeCall(
            p_url=api_url,
            data=json.dumps(data),
            method="POST"
        )

        response = json.loads(response.text)

        return response

    def showVersion(self):
        api_url = "/api/cli"
        data = {
            "commands": [
                "show version"
            ]
        }

        # pprint.pprint(json.dumps(data))
        response = self.makeCall(
            p_url=api_url,
            data=json.dumps(data),
            method="POST"
        )

        response = json.loads(response.text)
        version_info = response["response"]

        return version_info

    def enableVPN(self):
        api_url = "/api/cli"
        data = {
            "commands": [
            "webvpn",
            "enable outside",
            "write memory"
            ]
        }

        pprint.pprint(json.dumps(data))
        response = self.makeCall(
            p_url = api_url,
            data=json.dumps(data),
            method="POST"
        )

    def disableVPN(self):
        api_url = "/api/cli"
        data = {
            "commands": [
            "webvpn",
            "no enable outside",
            "write memory"
            ]
        }

        pprint.pprint(json.dumps(data))
        self.makeCall(
            p_url = api_url,
            data=json.dumps(data),
            method="POST"
        )

    def logoutVPN(self):
        api_url = "/api/cli"
        data = {
            "commands": [
            "vpn-sessiondb logoff anyconnect noconfirm"
            ]
        }

        pprint.pprint(json.dumps(data))
        self.makeCall(
            p_url = api_url,
            data=json.dumps(data),
            method="POST"
        )

        return

