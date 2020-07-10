#!/usr/bin/env python

import os
import sys
import shutil
import gi
from pymusiccast import McDevice
from pymusiccast.exceptions import YMCInitError
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class CfgButton(Gtk.VBox):
    ip_address = None
    success = None

    def __init__(self):
        self.cfg_path = os.path.expanduser('~/.gyrc')
        self.cfg_name = os.path.expanduser('~/.gyrc/gyrc.cfg')
        icon_dest = os.path.join(self.cfg_path, 'icons')
        os.makedirs(icon_dest, exist_ok=True)
        if not self.icon_install():
            print('unable to install icons from program_path/images')
            print('to ~/.gyrc/icons, please try copying them yourself.')
            print('')
        else:
            pass
            # print('icons in place')
        Gtk.VBox.__init__(self)
        if os.path.isfile(self.cfg_name):
            with open(self.cfg_name, 'r') as f:
                self.ip_address = f.readline()
            if self.ip_address:
                try:
                    self.success = McDevice(self.ip_address, udp_port=5006)
                except YMCInitError:
                    try:
                        os.remove(self.cfg_name)
                    except OSError:
                        pass
        label1 = Gtk.Label()
        label1.set_text(
            'Enter correct ip address or hostname for the Yamaha receiver:')
        self.pack_start(label1, True, True, 32)
        label2 = Gtk.Label()
        label2.set_text(
            'This app has no way of locating it')
        self.pack_start(label2, True, True, 32)
        label3 = Gtk.Label('ex: 192.168.x.xxx')
        self.pack_start(label3, True, True, 32)
        self.label4 = Gtk.Label('Success!')
        self.pack_start(self.label4, True, True, 32)
        self.label4.set_no_show_all(True)
        self.set_size_request(10, 10)
        self.button = Gtk.Button(label='ip')
        self.button.set_size_request(10, 10)
        self.set_border_width(64)
        self.button.set_tooltip_text('set receiver ip address or hostname')
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('ip address')
        self.entry.set_no_show_all(True)
        self.pack_start(self.button, False, False, 0)
        self.pack_start(self.entry, False, False, 0)
        self.button.connect('clicked', self.on_click, self.entry)
        self.win = Gtk.Window(title='Gyrc')
        self.win.connect('destroy', Gtk.main_quit)
        self.win.add(self)
        if not self.success:
            self.win.show_all()
            Gtk.main()

    def icon_install(self):
        icons = ('media-previous.png', 'media-stop.png', 'media-play.png',
                 'media-pause.png', 'media-next.png')
        srcpath = os.path.join(os.getcwd(), 'yrc/icons')
        if not os.path.isdir(srcpath):
            srcpath = os.path.join(os.getcwd(), 'icons')
        else:
            pass
        dstpath = os.path.expanduser('~/.gyrc/icons')
        if os.path.isdir(dstpath):
            if os.path.isfile(os.path.join(dstpath, 'media-play.png')):
                return True
        else:
            try:
                os.mkdir(dstpath)
            except OSError as e:
                print(e)
        if os.path.isdir(srcpath) and os.path.isdir(dstpath):
            for n in range(5):
                try:
                    icon = os.path.join(srcpath, icons[n])
                    shutil.copy(icon, dstpath)
                except OSError as e:
                    print(e)
                    return False
            return True
        return False

    def get_ip_address(self):
        with open(self.cfg_name, 'r') as f:
            self.ip_address = f.readline()
        return self.ip_address

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
        if not os.path.isdir(self.cfg_path):
            os.mkdir(self.cfg_path)
        with open(self.cfg_name, 'w') as f:
            f.write(self.ip_address)
        button.hide()
        self.label4.show()


def main():
    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    cfg_button = CfgButton()
    win.add(cfg_button)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
