#!/usr/bin/env python
import gi
from importlib import import_module
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')


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
