#!/usr/bin/env python3

import os
import gi
from .misc import IconInstaller
from gi.repository import GObject
from gi.repository import GLib
from importlib import import_module
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')
GdkPixbuf = import_module('gi.repository.GdkPixbuf')

power_icon = os.path.expanduser('~/.gyrc/icons/device-power.png')


class Expander(Gtk.Expander):
    def __init__(self, devbox):
        Gtk.Expander.__init__(self)
        self.set_size_request(-1, -1)
        self.connect('activate', self.on_expander_activated, devbox)

    def on_expander_activated(self, expander, devbox):
        if expander.get_expanded():
            devbox.hide()
            win = expander.get_parent().get_toplevel()
            win.resize(200, 100)
            win.queue_resize()
            win.show()
        else:
            devbox.show()


class DeviceBox(Gtk.VBox):
    def __init__(self, mcd_list):
        Gtk.VBox.__init__(self)
        self.set_size_request(-1, -1)
        if not os.path.isfile(power_icon):
            iconinstaller = IconInstaller()
            print(iconinstaller.icon_install())
        self.mcd_list = mcd_list
        self.create(mcd_list)

    def create(self, mcd_list):
        for n, mcd in enumerate(mcd_list):
            sliderbox = SliderBox(mcd_list, n)
            self.pack_start(sliderbox, False, False, 2)


class SliderBox(Gtk.HBox, GObject.GObject):
    index = -1

    def __init__(self, mcd_list, n):
        self.index = n
        Gtk.HBox.__init__(self)
        GObject.GObject.__init__(self)
        self.set_size_request(-1, -1)
        self.mcd_list = mcd_list
        self.mcd = self.mcd_list[self.index]
        self.zone = self.mcd_list.get_zone_list()[self.index]
        status = self.zone.get_status()
        self.prev_status = status
        self.max_volume = status['max_volume']
        print('max volume for this device is: ', self.max_volume)
        self.slider = Slider(self.zone)

        self.volUpBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_FORWARD,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volUpBtn.set_size_request(10, 10)
        self.volDnBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_BACK,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volDnBtn.set_size_request(10, 10)
        self.pack_start(self.volDnBtn, False, False, 0)
        self.pack_start(self.slider, False, False, 0)
        self.pack_start(self.volUpBtn, False, False, 0)
        self.mute_button = Gtk.CheckButton(label='mute')
        self.pack_start(self.mute_button, False, False, 2)
        self.mute_button.connect('toggled', self.on_mute_toggled)
        self.mute_state = status['mute']
        self.power_button = Gtk.ToggleButton()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            power_icon, 24, 24, GdkPixbuf.InterpType.BILINEAR)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.power_button.set_image(img)
        self.pack_start(self.power_button, False, False, 0)
        self.power_button.connect('toggled', self.on_power_toggled)
        self.power_state = status['power']
        self.power_button.set_active(status['power'])
        self.slider.connect('value-changed',
                            self.on_volume_adjusted)
        self.monitor()
        self.connect_object('mute-toggled',
                            self.toggle_mute_button,
                            self.mute_button)
        self.connect_object('power-toggled',
                            self.toggle_power_button,
                            self.power_button)
        self.connect_object('volume-adjusted',
                            self.adjust_slider,
                            self.slider)

    def adjust_slider(self, slider, value, *args):
        print('in adjust_slider ', value)
        slider.set_value(value)

    def on_volume_adjusted(self, slider, *args):
        print(slider.get_value())
        self.zone.set_volume(slider.get_value())

    def toggle_power_button(self, power_button, *args):
        status = self.zone.get_status()
        power_button.set_active(status['power'])

    def on_power_toggled(self, *args):
        self.zone.set_power(self.power_button.get_active())

    def on_mute_toggled(self, *args):
        self.zone.set_mute(self.mute_button.get_active())

    def toggle_mute_button(self, checkbutton, *args):
        status = self.zone.get_status()
        checkbutton.set_active(status['mute'])

    def monitor(self):
        GLib.timeout_add_seconds(1, self.checkit)

    def checkit(self):
        status = self.zone.get_status()
        if status['mute'] != self.prev_status['mute']:
            self.emit('mute-toggled', status['mute'])
        if status['volume'] != self.prev_status['volume']:
            print(type(status['volume']))
            self.emit('volume-adjusted', int(status['volume']))
        self.prev_status = status
        return True

    @GObject.Signal(name='mute-toggled',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=bool,
                    arg_types=(bool,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def mute_toggled(self, state, *args):
        return False

    @GObject.Signal(name='power-toggled',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=bool,
                    arg_types=(bool,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def power_toggled(self, state, *args):
        return False

    @GObject.Signal(name='volume-adjusted',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=int,
                    arg_types=(int,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def volume_adjusted(self, state, *args):
        return False


class Slider(Gtk.Scale, Gtk.Range, GObject.GObject):
    def __init__(self, zone):
        self.zone = zone
        self.max = self.zone.get_status()['max_volume']
        Gtk.Scale.__init__(self)
        Gtk.Range.__init__(self, 0, self.max)
        GObject.GObject.__init__(self)
        self.adjustment = Gtk.Adjustment(value=5.0,
                                         lower=0.0,
                                         upper=float(self.max),
                                         step_increment=1.0,
                                         page_increment=1.0,
                                         page_size=1.0)
        self.set_adjustment(self.adjustment)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_size_request(360, -1)
        self.set_fill_level(self.max * (4/5))
        self.set_has_origin(False)
        self.set_show_fill_level(True)
        self.set_can_focus(False)
        for n in range(0, self.max, 2):
            self.add_mark(n, Gtk.PositionType.TOP)
        self.set_current()

    def set_current(self):
        volume = self.zone.get_status()['volume']
        self.set_value(volume)
