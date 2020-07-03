#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import  Gtk


class PPSwitch(Gtk.Switch):
    def __init__(self, mcd):
        Gtk.Switch.__init__(self)
        self.mcd = mcd
        self.connect('state-set', self.on_clicked)

    def on_clicked(self, widget, state):
        if state is True:
            self.mcd.set_playback('play')
        elif state is False:
            self.mcd.set_playback('pause')
        return


class RecvrPower(Gtk.Switch):
    _state = None

    def __init__(self, yav):
        Gtk.Switch.__init__(self)
        Gtk.Switch.new()
        self.yav = yav
        self.connect('state-set', self.on_clicked)
        self.connect('activate', self.on_clicked, self.get_state())

    def on_clicked(self, widget, state):
        print('on click, state is ' + str(state))
        if state is True:
            self.yav.power_on()
        elif state is False:
            self.yav.power_standby()
        print('just toggled button')
        return False


