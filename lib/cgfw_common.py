#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import glob
import json
import socket
import ipaddress
import configparser
from gi.repository import GLib
from cgfw_util import CgfwUtil

class CgfwCommon:

    @staticmethod
    def getCgfwCfg():
        ret = dict()

        for cgfwFile in sorted(glob.glob("/etc/cgfw/*.cgfw")):
            cfg = configparser.SafeConfigParser()
            cfg.read(cgfwFile)

            if cfg.has_option("cgfw-entry", "provider"):
                provider = CgfwUtil.stripComment(cfg.get("cgfw-entry", "provider"))
                if provider not in ["myvpnpp"]:
                    raise Exception("invalid provider %s in cgfw-entry" % (provider))
                ret[provider] = dict()
            else:
                raise Exception("no type in cgfw-entry")

            if cfg.has_option("cgfw-entry", "username"):
                ret[provider]["username"] = CgfwUtil.stripComment(cfg.get("cgfw-entry", "username"))
            else:
                raise Exception("no username in cgfw-entry")

            if cfg.has_option("cgfw-entry", "password"):
                ret[provider]["password"] = CgfwUtil.stripComment(cfg.get("cgfw-entry", "password"))
            else:
                raise Exception("no password in cgfw-entry")

        return ret

    @staticmethod
    def getProvider(name, cfg, tmpDir, varDir):
        exec("from .provider.%s import Provider" % (name))
        return eval("Provider(cfg, tmpDir, varDir)")

    @staticmethod
    def getPrefixList(gfwDir):
        """Returns list of ipaddress.IPv4Network"""

        # get GFWed network list
        nets = []
        for fn in os.listdir(gfwDir):
            fullfn = os.path.join(gfwDir, fn)
            with open(fullfn) as f:
                lineList = f.read().split("\n")
                for i in range(0, len(lineList)):
                    line = CgfwUtil.getLineWithoutBlankAndComment(lineList[i])
                    if line is None:
                        continue
                    nets.append(ipaddress.IPv4Network(line))

        # optimize network list
        nets.sort()
        i = 0
        while i < len(nets):
            j = i + 1
            while j < len(nets):
                if nets[i].overlaps(nets[j]):
                    # big network is in front of small network, so we remove small network.
                    # I think network can only "wholly contain" each other, does "partly contain" really exist?
                    del nets[j]
                    continue
                j += 1
            i += 1

        return nets

    @staticmethod
    def getDomainList(gfwDomainDir):
        # get GFWed domain list
        ret = []
        for fn in os.listdir(gfwDomainDir):
            fullfn = os.path.join(gfwDomainDir, fn)
            with open(fullfn) as f:
                lineList = f.read().split("\n")
                for i in range(0, len(lineList)):
                    line = CgfwUtil.getLineWithoutBlankAndComment(lineList[i])
                    if line is None:
                        continue
                    ret.append(line)
        return ret


class CgfwCmdServer:

    def __init__(self, tmp_dir, up_callback, down_callback):
        self.upCallback = up_callback
        self.downCallback = down_callback
        self.serverFile = os.path.join(tmp_dir, "cmd.socket")
        self.cmdSock = None
        self.cmdSockWatch = None

    @property
    def server_file(self):
        return self.serverFile

    def run(self):
        self.cmdSock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.cmdSock.bind(self.serverFile)
        self.cmdSockWatch = GLib.io_add_watch(self.cmdSock, GLib.IO_IN, self._cmdServerWatch)

    def stop(self):
        if self.cmdSockWatch is not None:
            GLib.source_remove(self.cmdSockWatch)
            self.cmdSockWatch = None
        if self.cmdSock is not None:
            self.cmdSock.close()
            self.cmdSock = None
            os.unlink(self.serverFile)

    def _cmdServerWatch(self, source, cb_condition):
        buf = self.cmdSock.recvfrom(4096)[0].decode("utf-8")
        jsonObj = json.loads(buf)
        if jsonObj["cmd"] == "up":
            self.upCallback()
            return True
        elif jsonObj["cmd"] == "down":
            self.downCallback()
            return True
        else:
            assert False
