#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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

    def __init__(self, mcd):
        Gtk.Switch.__init__(self)
        Gtk.Switch.new()
        self.mcd = mcd
        self.connect('state-set', self.on_clicked)
        self.connect('activate', self.on_clicked, self.get_state())
        self.set_active(self.mcd.get_power_state())

    def on_clicked(self, widget, state):
        self.mcd.set_power_state(int(state))


'''
        print('on click, state is ' + str(state))
        if state is True:
            self.mcd.power_on()
        elif state is False:
            self.mcdi.power_standby()
        print('just toggled button')
        return False
'''
