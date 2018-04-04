#!/usr/bin/env python3

import os
import random


class Provider:

    @staticmethod
    def get_name():
        return "ershixiong"

    @staticmethod
    def get_description():
        return "None"

    @staticmethod
    def get_homepage():
        return "http://www.ershixiong1.mobi"

    def __init__(self, cfg, tmpDir, varDir):
        self.freeServerDict = {
            "Free-US-1": "167.88.179.15",
            "Free-US-2": "167.88.179.104",
        }
        self.vipServerDict = {
        }

        # "dine & dash" mode
        if "dine-and-dash" in cfg:
            if varDir is None:
                raise Exception("var directory is needed for \"dine-and-dash\" mode")
            self.dineAndDashMode = True
        else:
            self.dineAndDashMode = False

        # username & password
        if self.dineAndDashMode:
            userfile = os.path.join(varDir, "user.txt")
            with open(userfile, "r") as f:
                self.username = f.readline()
                self.password = f.readline()
            if self.username == "" or self.password == "":
                self.username, self.password = self._registerNew()
                with open(userfile, "w") as f:
                    f.write(self.username + "\n")
                    f.write(self.password + "\n")
        else:
            if "username" not in cfg:
                raise Exception("no \"username\" option in \"myvpnpp\" section")
            self.username = cfg["username"]

            if "password" not in cfg:
                raise Exception("no \"password\" option in \"myvpnpp\" section")
            self.password = cfg["password"]

        # select a server
        self.server = list(self.freeServerDict.keys())[random.randint(0, 1)]

    def switch_server(self):
        self.server = list(self.freeServerDict.keys())[random.randint(0, 1)]

    def get_server(self):
        optionTemplate = ""
        optionTemplate += "pty \"pptp %s --nolaunchpppd\"\n" % (self.freeServerDict[self.server])
        optionTemplate += "noauth\n"
        optionTemplate += "require-mppe\n"
        optionTemplate += "name %s\n" % (self.username)

        if self.dineAndDashMode:
            channel = "pptp-on-demand"
        else:
            channel = "pptp"

        return (self.server, channel, (optionTemplate, self.username, self.password))

    def _registerNew(self):
        raise Exception("failed to register new user")
