#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import errno
import ctypes
import base64
import shutil
import subprocess


class NewMountNamespace:

    _CLONE_NEWNS = 0x00020000               # <linux/sched.h>
    _MS_REC = 16384                         # <sys/mount.h>
    _MS_PRIVATE = 1 << 18                   # <sys/mount.h>
    _libc = None
    _mount = None
    _setns = None
    _unshare = None

    def __init__(self):
        if self._libc is None:
            self._libc = ctypes.CDLL('libc.so.6', use_errno=True)
            self._mount = self._libc.mount
            self._mount.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p]
            self._mount.restype = ctypes.c_int
            self._setns = self._libc.setns
            self._unshare = self._libc.unshare

        self.parentfd = None

    def __enter__(self):
        self.parentfd = open("/proc/%d/ns/mnt" % (os.getpid()), 'r')

        # copied from unshare.c of util-linux
        try:
            if self._unshare(self._CLONE_NEWNS) != 0:
                e = ctypes.get_errno()
                raise OSError(e, errno.errorcode[e])

            srcdir = ctypes.c_char_p("none".encode("utf_8"))
            target = ctypes.c_char_p("/".encode("utf_8"))
            if self._mount(srcdir, target, None, (self._MS_REC | self._MS_PRIVATE), None) != 0:
                e = ctypes.get_errno()
                raise OSError(e, errno.errorcode[e])
        except BaseException:
            self.parentfd.close()
            self.parentfd = None
            raise

    def __exit__(self, *_):
        self._setns(self.parentfd.fileno(), 0)
        self.parentfd.close()
        self.parentfd = None


def generateIpUpDownScript(fn, serverFile, upOrDown):
    with open(fn, "w") as f:
        buf = ""
        buf += "#!/usr/bin/python3\n"
        buf += "\n"
        buf += "import socket\n"
        buf += "import json\n"
        buf += "\n"
        buf += "data = {\"cmd\":\"%s\"}\n" % (upOrDown)
        buf += "sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)\n"
        buf += "sock.sendto(json.dumps(data).encode(\"utf-8\"), \"%s\")\n" % (serverFile)
        buf += "sock.close()\n"
        f.write(buf)
    subprocess.check_call(["/bin/chmod", "0755", fn])


assert len(sys.argv) == 8
serverFile = sys.argv[1]
onDemand = (sys.argv[2] != "0")
tmpDir = sys.argv[3]
gfwDir = sys.argv[4]
optionTemplate = base64.b64decode(sys.argv[5]).decode("ascii")
username = sys.argv[6]
password = sys.argv[7]

tmpEtcPppDir = os.path.join(tmpDir, "etc-ppp")
tmpChapSecretsFile = os.path.join(tmpEtcPppDir, "chap-secrets")
tmpIpUpScript = os.path.join(tmpEtcPppDir, "ip-up")
tmpIpDownScript = os.path.join(tmpEtcPppDir, "ip-down")
tmpPeerFile = os.path.join(tmpEtcPppDir, "peers", "cgfw")
proc = None

try:
    os.mkdir(tmpEtcPppDir)

    with open(tmpChapSecretsFile, "w") as f:
        buf = ""
        buf += "%s cgfw \"%s\" *\n" % (username, password)
        f.write(buf)
    subprocess.check_call(["/bin/chmod", "0600", tmpChapSecretsFile])

    generateIpUpDownScript(tmpIpUpScript, serverFile, "up")

    generateIpUpDownScript(tmpIpDownScript, serverFile, "down")

    os.mkdir(os.path.dirname(tmpPeerFile))
    with open(tmpPeerFile, "w") as f:
        buf = optionTemplate
        buf += "\n"
        buf += "lock\n"
        buf += "ifname cgfw\n"      # need ppp ifname patch exist on fpemud-refsystem but not on gentoo
        buf += "remotename cgfw\n"
        buf += "maxfail 1\n"        # upper layer can reconnect in a more flexible manner, such as switch to another server
        buf += "lcp-echo-interval 60\n"
        buf += "lcp-echo-failure 3\n"
        if onDemand:
            buf += "demand\n"
            buf += "idle 3600\n"
        f.write(buf)

    with NewMountNamespace():
        # pppd read config files from the fixed location /etc/ppp
        # this behavior is bad so we use mount namespace to workaround it
        subprocess.check_call(["/bin/mount", "--bind", tmpEtcPppDir, "/etc/ppp"])
        cmd = "/usr/sbin/pppd call cgfw nodetach"
        proc = subprocess.Popen(cmd, shell=True, universal_newlines=True)
        try:
            proc.wait()
        except KeyboardInterrupt:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()
except KeyboardInterrupt:
    pass
finally:
    if os.path.exists(tmpEtcPppDir):
        shutil.rmtree(tmpEtcPppDir)
    if proc is not None:
        sys.exit(proc.returncode)
