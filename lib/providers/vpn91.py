#!/usr/bin/env python3

import random


class Provider:

    @staticmethod
    def get_name():
        return "vpn91"

    @staticmethod
    def get_description():
        return "None"

    @staticmethod
    def get_homepage():
        return "https://www.vpn91.us"

    def __init__(self, cfg, tmpDir, varDir):
        self.testServerDict = {
            "US-SV-57": {
                "ip": "45.63.94.170",
                "username": "vpn1305",
                "password": "vpntm",
            },
            "US-SV-58": {
                "ip": "45.77.4.235",
                "username": "vpn6162",
                "password": "vpntm",
            },
        }

        # "dine & dash" mode, username, password
        if "dine-and-dash" in cfg:
            self.dineAndDashMode = True
        else:
            self.dineAndDashMode = False

            if "username" not in cfg:
                raise Exception("no \"username\" option in \"myvpnpp\" section")
            self.username = cfg["username"]

            if "password" not in cfg:
                raise Exception("no \"password\" option in \"myvpnpp\" section")
            self.password = cfg["password"]

        # select a server
        self.serverName = list(self.testServerDict.keys())[random.randint(0, 1)]

    def switch_server(self):
        self.serverName = list(self.testServerDict.keys())[random.randint(0, 1)]

    def get_server(self):
        if self.dineAndDashMode:
            username = self.testServerDict[self.serverName]["username"]
            password = self.testServerDict[self.serverName]["password"]
            channel = "pptp-on-demand"
        else:
            username = self.username
            password = self.password
            channel = "pptp"

        optionTemplate = ""
        optionTemplate += "pty \"pptp %s --nolaunchpppd\"\n" % (self.testServerDict[self.serverName]["ip"])
        optionTemplate += "noauth\n"
        optionTemplate += "require-mppe\n"
        optionTemplate += "name %s\n" % (username)

        return (self.serverName, channel, (optionTemplate, username, password))
