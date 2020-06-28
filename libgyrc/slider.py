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
        self.set_show_fill_level(True)
        for n in range(-80, 0, 2):
            self.add_mark(n, Gtk.PositionType.TOP)


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
