#!/usr/bin/env python

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Slider(Gtk.Scale, Gtk.Range):
    def __init__(self, min, max):
        Gtk.Scale.__init__(self)
        Gtk.Range.__init__(self, min, max)
        self.adjustment = Gtk.Adjustment(value=-40.0,
                                         lower=min,
                                         upper=max,
                                         step_increment=0.5,
                                         page_increment=0.5,
                                         page_size=1.0)
        self.set_adjustment(self.adjustment)
        self.min = min
        self.max = max
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_size_request(320, 10)
        self.set_fill_level(-30)
        self.set_has_origin(False)
        self.set_show_fill_level(True)
        for n in range(-80, 0, 2):
            self.add_mark(n, Gtk.PositionType.TOP)


class RadioBox(Gtk.HBox):
    def __init__(self, slider):
        Gtk.HBox.__init__(self)
        self.set_size_request(260, 10)
        self.pack_start(Gtk.Label(label='max vol: '), False, False, 0)
        radio = None
        for n, val in enumerate((-36.0, -24.0, -12.0, 0.0)):
            radio = Gtk.RadioButton.new_from_widget(radio)
            radio.connect('toggled',
                          self.max_radio_toggled,
                          val,
                          slider)
            self.pack_start(radio, False, False, 12)

    def max_radio_toggled(self, radio, val, slider):
        if radio.get_active():
            slider.set_fill_level(val)


class Win(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', Gtk.main_quit)
        self.set_default_size(400, 200)
        self.vbox = Gtk.VBox()
        self.vbox.set_size_request(300, 100)
        self.add(self.vbox)
        self.set_title('Volume')


def main():
    win = Win()
    slider = Slider(-80, 0.0)
    win.vbox.add(slider)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
