#!/usr/bin/env python3

import sys
import platform    # For getting the operating system name
import subprocess  # For executing a shell command


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


def main(host_ip):
    print(ping(host_ip))


if __name__ == '__main__':
    main(sys.argv[1])
