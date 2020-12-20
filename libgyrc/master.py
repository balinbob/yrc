#!/usr/bin/env python

import sys
import gi
from .devicebox import SliderBox
# from .mcd import DeviceList
from importlib import import_module
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')


'''class Slider(Gtk.Scale, Gtk.Range):
    def __init__(self, min, max):
        Gtk.Scale.__init__(self)
        Gtk.Range.__init__(self, min, max)
        print('self.min is: %s' % min)
        print('initializing self.max at %s' % max)
        self.min = min
        self.max = max
        self.adjustment = Gtk.Adjustment(value=64.0,
                                         lower=min,
                                         upper=float(max),
                                         step_increment=1.0,
                                         page_increment=1.0,
                                         page_size=1.0)
        self.set_adjustment(self.adjustment)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_size_request(320, 10)
        # self.set_fill_level(-36.0)
        self.set_has_origin(False)
        self.set_show_fill_level(True)
        self.set_can_focus(False)
        for n in range(0, 100, 2):
            self.add_mark(n, Gtk.PositionType.TOP)
        self.set_volume_limit(64.0)

    def set_volume_limit(self, limit):
        print('self.max is: %s' % self.max)
        print('main limit is: %s' % limit)
        self.set_fill_level(limit)
'''


class RadioBox(Gtk.HBox):
    def __init__(self, sliderbox):
        Gtk.HBox.__init__(self)
        self.sliderbox = sliderbox
        self.slider = sliderbox.slider
        self.set_size_request(20, 10)
        self.pack_start(Gtk.Label(label='max vol:                 '),
                        False, False, 0)
        radio = None
        self.radio_values = (64.0, 76.0, 88.0, 100.0)
        self.radio_value = {}
        self.active_limit = 64.0
        for n, val in enumerate(self.radio_values):
            radio = Gtk.RadioButton.new_from_widget(radio)
            radio.connect('toggled',
                          self.max_radio_toggled,
                          val,
                          self.slider)
            self.pack_start(radio, False, False, 11)
            radio.set_can_focus(False)
            self.radio_value.update({n: val})
        self.group = radio.get_group()
        self.group[0].set_active(True)

    def max_radio_toggled(self, radio, val, slider):
        if radio.get_active():
            print('max_radio_toggled val: ', val)
            self.slider.set_volume_limit(val)
            self.active_limit = val

    def get_radio_value(self):
        return self.active_limit

    def get_volume_limit(self):
        return self.active_limit


class Master(Gtk.VBox):
    def __init__(self, mcd_list):
        Gtk.VBox.__init__(self)
        self.mcd_list = mcd_list
        self.set_size_request(-1, -1)
        self.sliderbox = SliderBox(self.mcd_list, 0)
        self.slider = self.sliderbox.slider
        # self.radiobox = RadioBox(self.sliderbox)
        print('in master')
        self.hbox = Gtk.HBox()
        self.hbox.set_size_request(320, 10)
        self.hbox.pack_start(self.sliderbox, False, False, 0)
        self.pack_start(self.hbox, False, False, 0)
        self.hbox2 = Gtk.HBox()
        self.hbox2.set_size_request(60, 10)
        # self.hbox2.pack_start(self.radiobox, False, False, 0)
        self.pack_start(self.hbox2, False, False, 0)


class Win(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', Gtk.main_quit)
        self.set_default_size(360, 200)
        self.set_title('Master Control')


def main():
    win = Win()
    box = Master()
    win.add(box)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
