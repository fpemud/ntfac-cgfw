#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import signal
import logging
from gi.repository import GLib
from cgfw_util import CgfwUtil
from cgfw_common import CgfwCommon
from cgfw_common import CgfwCmdServer


class CgfwMain:

    def __init__(self, param):
        self.param = param
        self.mainloop = None

        self.curProviderList = []

        self.vpnRestartTimer = None
        self.vpnClientProc = None
        self.vpnClientPidWatch = None
        self.upCalled = None

        self.cmdServer = CmdServer(self.param.tmpDir, self._upCallback, self._downCallback)

    def run(self):
        try:
            logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
            logging.getLogger().setLevel(CgfwUtil.getLoggingLevel(self.param.logLevel))
            logging.info("Program begins.")

            # read configuration
            for section, data in CgfwCommon.getCgfwCfg().items():
                tmpDir2 = os.path.join(self.param.tmpDir, section)
                if self.varDir is None:
                    varDir2 = None
                else:
                    varDir2 = os.path.join(self.param.varDir, section)
                self.curProviderList.append(CgfwCommon.getProvider(section, data, tmpDir2, varDir2))

            # create main loop
            mainloop = GLib.MainLoop()

            # start business
            if not os.path.exists(self.param.tmpDir):
                os.makedirs(self.param.tmpDir)
            self.vpnRestartTimer = GObject.timeout_add_seconds(0, self._vpnRestartTimerCallback)

            # start main loop
            logging.info("Mainloop begins.")
            GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGINT, on_sig_int, None)
            GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, on_sig_term, None)
            mainloop.run()
            logging.info("Mainloop exits.")
        finally:
            logging.shutdown()

    def _sigHandlerINT(self, signum):
        logging.info("SIGINT received.")
        self.mainloop.quit()
        return True

    def _sigHandlerTERM(self, signum):
        logging.info("SIGTERM received.")
        self.mainloop.quit()
        return True

    def _vpnRestartTimerCallback(self):
        try:
            try:
                self.cmdServer.run()
                self._runVpnClient()
                self.upCalled = False
                self.vpnRestartTimer = None
            except Exception as e:
                self._stopVpnClient()
                self.cmdServer.stop()
                self.upCalled = None
                self.vpnRestartTimer = GObject.timeout_add_seconds(self.param.vpnRestartInterval, self._vpnRestartTimerCallback)
                raise
        except:
            self.errorCallback("VPN restart timer triggered", traceback.format_exc())
        finally:
            return False

    def _vpnChildWatchCallback(self, pid, condition):
        try:
            assert pid == self.vpnClientProc.pid

            if self.upCalled:
                self.changeCallback(dict())
            self._stopVpnClient()
            self.cmdServer.stop()
            self.vpnRestartTimer = GObject.timeout_add_seconds(self.param.vpnRestartInterval, self._vpnRestartTimerCallback)
        except:
            self.errorCallback("VPN child watch triggered", traceback.format_exc())

    def _runVpnClient(self):
        selfDir = os.path.dirname(os.path.realpath(__file__))

        self.curProviderList[0].switch_server()
        serverName, channel, parameters = self.curProviderList[0].get_server()

        # start vpn client process
        if channel in ["pptp", "pptp-on-demand"]:
            optionTemplate, username, password = parameters
            self.vpnClientProc = subprocess.Popen([
                "/usr/bin/python3",
                os.path.join(selfDir, "subproc_pptp.py"),
                self.cmdServer.server_file,
                "0" if channel == "pptp" else "1",
                self.param.tmpDir,
                self.param.gfwDir,
                base64.b64encode(optionTemplate.encode("ascii")),
                username,
                password,
            ])
        else:
            assert False
        self.vpnClientPidWatch = GLib.child_watch_add(self.vpnClientProc.pid, self._vpnChildWatchCallback)

        # wait for interface
        i = 0
        while True:
            if "cgfw" not in netifaces.interfaces() or netifaces.AF_INET not in netifaces.ifaddresses("cgfw"):
                if i >= 10:
                    raise Exception("Interface allocation time out.")
                time.sleep(1.0)
                i += 1
                continue
            break

    def _stopVpnClient(self):
        if self.vpnClientPidWatch is not None:
            GLib.source_remove(self.vpnClientPidWatch)
            self.vpnClientPidWatch = None
        if self.vpnClientProc is not None and self.vpnClientProc.poll() is None:
            self.vpnClientProc.send_signal(signal.SIGINT)
            self.vpnClientProc.wait()
            self.vpnClientProc = None

    def _upCallback(self):
        serverName, dummy, dummy = self.curProviderList[0].get_server()
        logging.info("CGFW VPN %s connected." % (serverName))

        CgfwCommon.ntfacSendEntityNameserverNew(self.param.nameServerList, CgfwCommon.getDomainList(self.param.gfwDomainDir))
        CgfwCommon.ntfacSendEntityGatewayNew((None, "cgfw"), [x.with_netmask for x in CgfwCommon.getPrefixList(self.param.gfwDir)])

        self.upCalled = True

    def _downCallback(self):
        serverName, dummy, dummy = self.curProviderList[0].get_server()
        logging.info("CGFW VPN %s disconnected." % (serverName))
