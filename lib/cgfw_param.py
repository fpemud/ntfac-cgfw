#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os


class CgfwParam:

    def __init__(self):
        self.libDir = "/usr/lib/ntfac-cgfw"
        self.logDir = "/var/log/ntfac-cgfw"
        self.tmpDir = "/tmp/ntfac-cgfw"
        self.etcDir = "/etc/cgfw"

        self.dataDir = "/usr/share/ntfac-cgfw"
        self.gfwDir = os.path.join(self.dataDir, "gfw.d")
        self.gfwDomainDir = os.path.join(self.dataDir, "gfw-domain.d")
        self.hostsDir = os.path.join(self.dataDir, "hosts.d")

        self.nameServerList = ["8.8.8.8", "8.8.4.4"]
        self.vpnRestartInterval = 60        # in seconds

        self.logLevel = None
