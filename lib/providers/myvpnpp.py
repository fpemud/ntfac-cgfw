#!/usr/bin/env python3

import random


class Provider:

    @staticmethod
    def get_name():
        return "myvpnpp"

    @staticmethod
    def get_description():
        return "None"

    @staticmethod
    def get_homepage():
        return "http://uvpnpp.org"

    def __init__(self, cfg, tmpDir, varDir):
        # "dine & dash" mode
        if "dine-and-dash" in cfg:
            raise Exception("\"dine-and-dash\" mode is not supported")

        # username & password
        if True:
            if "username" not in cfg:
                raise Exception("no \"username\" option in \"myvpnpp\" section")
            self.username = cfg["username"]

            if "password" not in cfg:
                raise Exception("no \"password\" option in \"myvpnpp\" section")
            self.password = cfg["password"]

        # select a server
        self.server = None
        self.switch_server()

    def switch_server(self):
        num = None
        while True:
            num = random.randint(4, 9)
            if num == 1:                    # vip-1.uvpnpp.org seems bad
                continue
            if num == 2:                    # vip-2.uvpnpp.org seems bad
                continue
            if num == 3:                    # vip-3.uvpnpp.org seems bad
                continue
            if num == 5:                    # it seems pushing to github often fail when vip-5.uvpnpp.org is used
                continue
            if num == 6:                    # vip-6.uvpnpp.org seems bad
                continue
            break
        self.server = "vip-%d.uvpnpp.org" % (num)

    def get_server(self):

        optionTemplate = ""
        optionTemplate += "pty \"pptp %s --nolaunchpppd\"\n" % (self.server)
        optionTemplate += "noauth\n"
        optionTemplate += "require-mppe\n"
        optionTemplate += "name %s\n" % (self.username)

        return (self.server, "pptp", (optionTemplate, self.username, self.password))
