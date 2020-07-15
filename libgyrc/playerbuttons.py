#!/usr/bin/env python

import os
import sys
import gi
from gi.repository import GLib
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf
from gi.repository import Gtk


class PlayerButtons(Gtk.ButtonBox):
    icon_path = os.path.expanduser('~/.gyrc/icons/')
    icons = ('media-previous.png', 'media-stop.png', 'media-play.png',
             'media-pause.png', 'media-next.png')

    def __init__(self, mcd):
        Gtk.ButtonBox.__init__(self)
        self.mcd = mcd
        self.set_size_request(10, 10)
        self.set_layout(Gtk.ButtonBoxStyle.START)
        self.buttonlist = []
        for n in range(5):
            button = Gtk.ToggleButton()
            self.buttonlist.append(button)
            button.set_size_request(32, 32)
            icon = os.path.join(self.icon_path, self.icons[n])
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                                icon, 36, 36, GdkPixbuf.InterpType.BILINEAR)
            img = Gtk.Image.new_from_pixbuf(pixbuf)
            button.set_image(img)
            self.pack_start(button, False, False, 0)

        self.back = self.buttonlist[0]
        self.stop = self.buttonlist[1]
        self.play = self.buttonlist[2]
        self.pause = self.buttonlist[3]
        self.next = self.buttonlist[4]

        self.back_id = self.back.connect('toggled', self.on_back_button)
        self.pause_id = self.pause.connect('toggled', self.on_pause_button)
        self.stop_id = self.stop.connect('toggled', self.on_stop_button)
        self.play_id = self.play.connect('toggled', self.on_play_button)
        self.next_id = self.next.connect('toggled', self.on_next_button)

        self.mcd.connect('playback-changed',
                         self.on_playback_changed,
                         self.mcd.playback)

        GLib.timeout_add_seconds(1, self.initialize)

    def initialize(self):
        print('initializing')
        info = self.mcd.get_play_info()
        if info['playback'] == 'play':
            self.play.set_active(True)
            self.pause.set_active(False)
        elif info['playback'] == 'pause':
            with self.pause.handler_block(self.pause_id):
                self.pause.set_active(True)
        elif info['playback'] == 'stop':
            with self.stop.handler_block(self.stop_id):
                self.stop.set_active(True)
        return False

    def on_playback_changed(self, mcd, playback, arg):
        print(playback)
        print(arg)
        self.pause.handler_block(self.pause_id)
        self.stop.handler_block(self.stop_id)
        self.play.handler_block(self.play_id)

        self.pause.set_active(False)
        self.stop.set_active(False)
        self.play.set_active(False)

        if playback == 'pause':
            self.pause.set_active(True)
        if playback == 'stop':
            self.stop.set_active(True)
        if playback == 'play':
            self.play.set_active(True)

        self.pause.handler_unblock(self.pause_id)
        self.stop.handler_unblock(self.stop_id)
        self.play.handler_unblock(self.play_id)

    def on_next_button(self, button, arg=None):
        print('next button')
        if button.get_active():
            print('next')
            self.mcd.set_playback('next')
            with self.next.handler_block(self.next_id):
                self.next.set_active(False)
        else:
            print('next button up')

    def on_back_button(self, button, arg=None):
        print('back button')
        print('arg is %s' % arg)
        if button.get_active():
            print('back')
            self.mcd.set_playback('previous')
            with self.back.handler_block(self.back_id):
                self.back.set_active(False)
        else:
            print('back button up')

    def on_pause_button(self, button, arg=None):
        print('pause button')
        if button.get_active():
            print('pause')
            self.mcd.set_playback('pause')
            with self.pause.handler_block(self.pause_id):
                self.pause.set_active(False)
            with self.play.handler_block(self.play_id):
                self.play.set_active(False)
        else:
            print('play')
            self.mcd.set_playback('play')
            with self.pause.handler_block(self.pause_id):
                self.play.set_active(True)

    def on_stop_button(self, button, arg=None):
        print('stop button')
        if button.get_active():
            self.mcd.set_playback('stop')
            with self.pause.handler_block(self.pause_id):
                self.pause.set_active(False)
            with self.play.handler_block(self.play_id):
                self.play.set_active(False)
            with self.stop.handler_block(self.stop_id):
                self.stop.set_active(False)

    def on_play_button(self, button, arg=None):
        print('play button')
        if button.get_active():
            print('play')
            self.mcd.set_playback('play')
            with self.pause.handler_block(self.pause_id):
                self.pause.set_active('False')
            with self.play.handler_block(self.play_id):
                self.play.set_active('False')
        if self.mcd.get_play_info()['playback'] == 'play':
            with self.play.handler_block(self.play_id):
                self.pause.set_active('False')


def main():
    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    bbox = PlayerButtons()
    win.add(bbox)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
