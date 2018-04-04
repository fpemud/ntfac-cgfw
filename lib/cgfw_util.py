#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import re
import json

class CgfwUtil:

    @staticmethod
    def stripComment(s):
        m = re.search("(.*?) *#.*", s)
        if m is not None:
            return m.group(1)
        else:
            return s

    @staticmethod
    def getLineWithoutBlankAndComment(line):
        if line.find("#") >= 0:
            line = line[:line.find("#")]
        line = line.strip()
        return line if line != "" else None

    @staticmethod
    def ntfacSendEntityNameserverNew(id, target, domainList):
        msg = {
            "operation": "new",
            "id": id,
            "type": "nameserver",
            "data": {
                "target": target,
                "domain-list": domainList,
            },
        }
        print(json.dumps(msg) + "\n")

    @staticmethod
    def ntfacSendEntityGatewayNew(id, target, networkList):
        msg = {
            "operation": "new",
            "id": id,
            "type": "gateway",
            "data": {
                "target": target,
                "network-list": networkList,
            },
        }
        print(json.dumps(msg) + "\n")
