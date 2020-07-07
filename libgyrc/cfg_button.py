#!/usr/bin/env python

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class CfgButton(Gtk.HBox):
    def __init__(self):
        self.cfg_name = os.path.expanduser('~/.gyrc.cfg')
        Gtk.HBox.__init__(self)
        if os.path.isfile(self.cfg_name):
            with open(self.cfg_name) as f:
                self.ip_address = f.read()
                if self.ip_address:
                    self.set_no_show_all(True)
                    print(self.ip_address)
                    return
        self.set_size_request(10, 10)
        self.button = Gtk.Button(label='ip')
        self.button.set_size_request(10, 10)
        self.button.set_border_width(0)
        self.set_border_width(0)
        self.button.set_tooltip_text('set receiver ip address or hostname')
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('ip address')
        self.entry.set_no_show_all(True)
        self.pack_start(self.button, False, False, 0)
        self.pack_start(self.entry, False, False, 0)
        self.button.connect('clicked', self.on_click, self.entry)

    def on_click(self, button, entry):
        entry.set_focus_on_click(True)
        self.buffer = Gtk.EntryBuffer()
        entry.set_buffer(self.buffer)
        entry.show()
        button.hide()
        entry.connect('activate', self.on_entry_done, button)

    def on_entry_done(self, entry, button):
        entry.hide()
        button.show()
        self.ip_address = self.buffer.get_text()
        print(self.ip_address)
        with open(self.cfg_name, 'w') as f:
            f.write(self.ip_address)
        button.hide()


def main():
    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    cfg_button = CfgButton()
    win.add(cfg_button)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
