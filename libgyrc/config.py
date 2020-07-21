#!/usr/bin/env python3

import os
import sys
import shutil
import gi

from ping import ping
# from json.decoder import JSONDecodeError
from importlib import import_module
from mcd import MCD
# from pymusiccast import McDevice
# from pymusiccast.exceptions import YMCInitError
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')

cfg_name = os.path.expanduser('~/.gyrc/gyrc.cfg')
cfg_path = os.path.expanduser('~/.gyrc')
mcd_list = []
ip_list = []


class Config(object):
    window = None

    def __init__(self):
        self.cfg_path = os.path.expanduser('~/.gyrc')
        self.cfg_name = os.path.expanduser('~/.gyrc/gyrc.cfg')
        # self.icon_dest = os.path.join(self.cfg_path, 'icons')

    def install_icons(self):
        icon_dest = os.path.join(os.path.expanduser('~/.gyrc'), 'icons')
        os.makedirs(icon_dest, exist_ok=True)
        if not icon_install():
            print('unable to install icons!')
            print('Please cppy icons from program_path/images')
            print('to ~/.gyrc/icons')
            print('')

    def run(self):
        self.window = Window()
        self.window.config = self
        self.window.show_all()
        Gtk.main()

    def get_config(self):
        global ip_list
        global mcd_list

        try:
            with open(cfg_name, 'r') as f:
                ip_list = f.readlines()
            for n, ip in enumerate(ip_list):
                ip_list[n] = ip.strip('\n')
        except FileNotFoundError:
            config = Config()
            config.run()
        finally:
            return ip_list


def get_mcd_list():
    if mcd_list:
        return mcd_list
    else:
        return None


def icon_install():
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


class WidgetBox(Gtk.VBox):
    strings = ['Receiver', '2nd',
               '3rd device', '4th device', '5th device']
    ip_list = []
    entries = []
    buttons = []
    boxes = []

    def __init__(self, window, instance=0):
        Gtk.VBox.__init__(self)
        self.window = window
        self.instance = instance
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('ip address')
        self.text_buffer = Gtk.EntryBuffer()
        self.entry.set_buffer(self.text_buffer)
        self.entry.name = ('entry %d' % instance)
        self.entry.set_no_show_all(True)
        self.entries.append(self.entry)
        self.entry.connect('activate', self.on_entry, instance)

        self.button = Gtk.Button(label='enter ' + self.strings[instance] + (' device' if instance > 0 else '') + ' ip address')
        # self.button.set_label('enter ' + self.strings[instance] +
        #                      ' device' if instance > 0 else '' +
        #                      ' ip address')
        self.buttons.append(self.button)
        self.button.connect('clicked', self.on_button, self.entry, instance)
        self.button.name = ('button %d' % instance)
        self.button.set_no_show_all(True)
        self.pack_start(self.entry, False, False, 4)
        self.pack_start(self.button, False, False, 4)

    def on_entry(self, entry, instance):
        self.button.emit('clicked')

    def on_button(self, button, entry, instance):
        ip = entry.get_buffer().get_text()
        if ip not in ip_list:
            validator = Ip4Validator(ip)
            if validator.result and ping(ip):
                mcd = MCD(None, ip)
                if not mcd:
                    sys.exit(255)
                else:
                    ip_list.append(ip)
                    mcd_list.append(mcd)
            else:
                entry.set_text('')
                entry.set_placeholder_text('enter valid ipv4 address...')
                button.grab_focus()
        else:
            entry.set_text('')
            entry.set_placeholder_text('already connected...')
            button.grab_focus()
        if len(ip_list) > instance:
            print(ip_list)
            if len(self.strings) > instance:
                self.entries[self.instance+1].show()
                self.buttons[self.instance+1].show_now()
                self.entries[self.instance+1].grab_focus()
            print(self.instance+1)
            print(self.entries[self.instance+1].name)


class Ip4Validator():
    def __init__(self, ip):
        self.result = self.validate(ip)

    def validate(self, ip):
        return(ip.count('.') == 3 and all(self.valid_ip(int(s))
                                          for s in ip.split('.')))

    def valid_ip(self, i):
        return(0 <= i <= 255)


class Window(Gtk.Window):
    instance = 0
    entries = []
    buttons = []
    boxes = []
    done = False

    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', Gtk.main_quit)

        self.cfg_path = os.path.expanduser('~/.gyrc')
        self.cfg_name = os.path.expanduser('~/.gyrc/gyrc.cfg')

        self.frame = Gtk.VBox()
        self.frame.name = 'frame'
        self.add(self.frame)
        self.set_default_size(240, 20)
        self.instance = 0
        button_done = Gtk.Button(label='Done')
        button_done.connect('clicked', self.on_button_done)
        self.frame.pack_end(button_done, False, False, 12)
        for instance in range(5):
            widget_box = WidgetBox(self, instance)
            widget_box.name = 'widget box'
            self.boxes.append(widget_box)
            self.frame.pack_start(widget_box, False, False, 8)
        for child in self.boxes[0].get_children():
            child.show_now()

    def on_button_done(self, button, *args):
        print('on done!')
        for n, ip in enumerate(ip_list):
            ip_list[n] = ip + '\n'
        print(ip_list)
        if not os.path.isdir(self.cfg_path):
            try:
                os.mkdir(self.cfg_path)
            except OSError as e:
                print(e)
        try:
            with open(self.cfg_name, 'w') as f:
                f.writelines(ip_list)
        except IOError as e:
            print(e)
        except OSError as e:
            print(e)
        self.destroy()


def main():
    cfg = Config()
    cfg.run()


if __name__ == '__main__':
    sys.exit(main())
