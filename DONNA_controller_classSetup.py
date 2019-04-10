# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 13:30:15 2019

@author: Sergey Koryakin
"""
# importing EEG interface modules...
import sys
import json
from websocket import create_connection
import ssl
import time


class EPOC_Interface:
    def __init__(self, username, password, licensekey, client_id, client_secret, authorization):
        self.ws = create_connection("wss://emotivcortex.com:54321", sslopt={"cert_reqs": ssl.CERT_NONE})
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.key = licensekey
        self._auth = authorization

    def sendMethod(self, method, params, returnOutput=False):
        self.ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
          }))
        if returnOutput:
            return str(self.ws.recv())
        else:
            print('WEBSOCKET OUTPUT:\n', self.ws.recv())

    def logout(self):
        method = "logout"
        params = {"username": self.username}
        self.sendMethod(method, params)

    def login(self):
        method = "login"
        params = {"username": self.username, "password": self.password, "client_id": self.client_id, "client_secret": self.client_secret}
        self.sendMethod(method, params)

    def authorize(self):
        method = "authorize"
        params = {"client_id": self.client_id, "client_secret": self.client_secret, "license": self.key, "debit": 10}
        resp = self.sendMethod(method, params, returnOutput=True)
        print('WEBSOCKET OUTPUT:\n', resp)
        authStart = resp.find("_auth")+8;
        authEnd = len(resp)-3;
        self._auth = resp[authStart:authEnd];
        print("!!!!!!\nAuthorization code:\n", self._auth, "\n!!!!!!")
        #  is below line necessary again?
        # print('WEBSOCKET OUTPUT:\n',self.ws.recv())
    # Create a session with the Emotiv EPOC

    def createSession(self, recordData=False):
        method = "createSession"
        if recordData:
            rID = "c7030f18-4b0f-4a6d-b953-a2b16edd217e"
#            start = "2019-03-05T16:20:00.994326+07:00"
#            start = "2017-06-01T15:22:33.906495+07:00"
#            end = "2017-06-01T15:25:33.906495+07:00"
            logs = {"recordInfos": [{"name": "demo", "notes": "test1", "recordId": rID, "subject": "sub2"}]}
#            , "sampleMarkerAFF": [174,239],
#                                     "sampleMarkerEEG": [11140,15324],"startMarkerRecording": start,
#                                     "stopMarkerRecording": end
            params = {"_auth": self._auth, "status": "open", "recording": True, "logs": logs, "streams": ["eeg"]}
        else:
            params = {"_auth": self._auth, "status": "open", "streams": ["eeg"]}
        self.sendMethod(method, params)
        print("Session created...")

    def subsribe(self, stream):
        method = "subscribe"
        params = {"_auth": self._auth, "streams": [stream]}
        self.sendMethod(method, params)

    def unsubsribe(self, stream):
        method = "unsubscribe"
        params = {"_auth": self._auth, "streams": [stream]}
        self.sendMethod(method, params)

    def train(self, command):
        method = "training"
        params_start = {"_auth": self._auth, "detection": "mentalCommand", "action": command, "status": "start"}
        self.sendMethod(method, params_start)
        time.sleep(5)
        print('WEBSOCKET OUTPUT:\n', self.ws.recv())
        time.sleep(10)
        print('WEBSOCKET OUTPUT:\n', self.ws.recv())
        params_accept = {"_auth": self._auth, "detection": "mentalCommand", "action":command, "status": "accept"}
        self.sendMethod(method, params_accept)
        time.sleep(2)
        print('WEBSOCKET OUTPUT:\n', self.ws.recv())

