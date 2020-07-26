#!/usr/bin/env python3

import os
import shutil
import platform    # For getting the operating system name
import subprocess  # For executing a shell command


icons = ('media-previous.png', 'media-stop.png', 'media-play.png',
         'media-pause.png', 'media-next.png', 'device-power.png')


class IconInstaller(object):
    def __init__(self):
        pass

    def icon_install(self):
        srcpath = os.path.join(os.getcwd(), 'yrc/icons')
        if not os.path.isdir(srcpath):
            srcpath = os.path.join(os.getcwd(), 'icons')
        else:
            pass

        dstpath = os.path.expanduser('~/.gyrc/icons')
        try:
            os.makedirs(dstpath, exist_ok=True)
        except OSError as e:
            print(e)
        if os.path.isdir(srcpath) and os.path.isdir(dstpath):
            for icon in icons:
                try:
                    if not os.path.isfile(os.path.join(dstpath, icon)):
                        icon = os.path.join(srcpath, icon)
                        shutil.copy(icon, dstpath)
                except OSError as e:
                    print(e)
                    return False
            return True
        return False


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP)
    request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', '-q', host]

    return subprocess.call(command) == 0
