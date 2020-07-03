#!/usr/bin/env python
import sys
import threading
from pymusiccast import McDevice
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class YMonitor(McDevice):
    def __init__(self, host='yamaha', port=5006):
        MCDevice.__init__(self, host, port)
        self.new_info = self.get_play_info()
        self.play_info = self.new_info
        self.handle_status()


    def run(self):
        while True:
            self.msg = self.messages.get()
            if 'netusb' in self.msg:
                self.new_info = self.get_play_info()
                if self.new_info != self.play_info:
                    self.play_info = self.new_info
        return False

