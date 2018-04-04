#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import shutil
import cgfw
import time
from gi.repository import GLib


def on_notify(notify_obj):
    print("abc")


try:
    os.mkdir("/tmp/cgfw")

    cfg = dict()
    cfg["tmp-directory"] = "/tmp/cgfw"

    cfg["provider"] = dict()    
    cfg["provider"]["myvpnpp"] = dict()
    cfg["provider"]["myvpnpp"]["username"] = "abc"
    cfg["provider"]["myvpnpp"]["password"] = "abc"
    cgfw.start(cfg, on_notify)
    print("started.")

    GLib.MainLoop().run()
finally:
    shutil.rmtree("/tmp/cgfw")
