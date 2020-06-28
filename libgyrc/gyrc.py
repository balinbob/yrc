#!/usr/bin/env python

import sys
# import time
from yamaha_av import YamahaAV
from pymusiccast import McDevice
from urllib.parse import quote
import gi
from gi.repository import GObject
from gi.repository import GLib
from slider import Slider
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
gi.require_version('Pango', '1.0')
from gi.repository.Pango import EllipsizeMode
# ip = '192.168.1.130'


def boolit(state):
    return (True if state == 'On' else False)


def new_volume_slider():
    slider = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, -80, 0, 2)
    for n in range(-80, 0, 2):
        slider.add_mark(n, Gtk.PositionType.BOTTOM)
    slider.set_digits(1)
    slider.set_draw_value(True)
    slider.set_value_pos(Gtk.PositionType.TOP)
    slider.set_size_request(320, 18)
    slider.set_increments(0.5, 0.5)
    slider.set_sensitive(False)
    return slider


class YamaWin(Gtk.Window):
    ip = '192.168.1.130'
    vol_pressed = False

    def __init__(self):

        Gtk.Window.__init__(self, title='Gyrc')
        self.mcd = MCD(self, self.ip)
        self.yav = YAV(self, self.ip)
        self.yav.setup()

        self.recvState = self.yav.get_status_string('Power')
        self.recvPower = RecvrPower(self.yav)
        label = Gtk.Label.new_with_mnemonic('Po_wer')
        label.set_text('Power')
        label.set_mnemonic_widget(self.recvPower)
        self.recvPower.add_mnemonic_label(Gtk.Label.new_with_mnemonic('_B'))
        grid = Gtk.Grid()
        self.set_default_size(640, 320)
        self.add(grid)
#        hspacer = Gtk.Box()
#        hspacer.set_width = 16
        vspacer = Gtk.Box()
        vspacer.set_size_request(32, 120)
        grid.set_column_spacing(10)
        grid.set_row_spacing(4)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(self.recvPower, 2, 0, 1, 1)
#        grid.attach(hspacer, 1, 0, 2, 2)
#        grid.attach(vspacer, 0, 1, 12, 1)
#        self.volSlider = new_volume_slider()
        self.volSlider = Slider(-80, 0.0)
        self.volSlider.set_size_request(380, 10)
#        grid.attach(self.volSlider, 4, 0, 12, 1)
        self.volUpBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_FORWARD,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volUpBtn.set_size_request(10, 10)
        self.volDnBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_BACK,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volDnBtn.set_size_request(10, 10)

        slider_box = Gtk.HBox()
        slider_box.set_size_request(400, 10)
        slider_box.pack_start(self.volDnBtn, True, True, 0)
        slider_box.pack_start(self.volSlider, True, True, 0)
        slider_box.pack_start(self.volUpBtn, True, True, 0)

#        grid.attach(self.volUpBtn, 18, 0, 1, 1)
#        grid.attach(self.volDnBtn, 3, 0, 1, 1)
        grid.attach(slider_box, 3, 0, 16, 1)

        self.info_box = Gtk.VBox()
        self.info_box.set_size_request(10, 10)
        self.labels = []
        for n in range(3):
            self.labels.append(Gtk.Label())
            self.labels[n].set_halign(Gtk.Align.START)
            self.labels[n].set_ellipsize(EllipsizeMode.END)
#            spacer = Gtk.Box()
#            spacer.set_size_request(20, 4)
            hbox = Gtk.HBox()
#            hbox.add(spacer)
            hbox.pack_start(self.labels[n], True, True, 4)
            self.info_box.pack_start(hbox, True, False, 8)

        self.mcd.checkit()
        grid.attach(self.info_box, 1, 4, 15, 1)
        print('---')
        print(self.recvState)
        self.volSlider.set_value(self.yav.get_volume())
        self.recvPower.set_state(boolit(self.recvState))
        self.yav.monitor()
        self.mcd.monitor()
        self.yav.connect('changed', self.set_power)
        self.recvPower.connect('state-set', self.pwr_cb)
        self.volhandler = self.volSlider.connect('value-changed',
                                                 self.volslider_changed)
        self.volslider_id = self.yav.connect('adjust',
                                             self.adjust_volslider)
        self.volUpBtn.connect('button-press-event',
                              self.volbtn_click,
                              (self.volSlider.get_value(),
                               self.yav.get_volume()))

        self.volUpBtn.connect('button-release-event',
                              self.volbtn_click,
                              (self.volSlider.get_value(),
                               self.yav.get_volume()))

        self.volDnBtn.connect('button-press-event',
                              self.volbtn_click,
                              (self.volSlider.get_value(),
                               self.yav.get_volume()))

        self.volDnBtn.connect('button-release-event',
                              self.volbtn_click,
                              (self.volSlider.get_value(),
                               self.yav.get_volume()))

#        self.volUpBtn.connect_object('clicked', self.vol_up, self.volSlider)
#        self.volDnBtn.connect_object('clicked', self.vol_down, self.volSlider)

#        print(self.mcd.get_play_info())

    def vol_up(self, volslider):
        value = volslider.get_value()
        volslider.set_value(value + 0.5)
        self.yav.increase_volume(zone=0, inc=0.5)

    def vol_down(self, volslider):
        value = volslider.get_value()
        volslider.set_value(value - 0.5)
        self.yav.decrease_volume(zone=0, dec=0.5)

    def set_power(self, yav, status, *args):
        self.recvState = status
        self.recvPower.set_state(self.recvState)
        return True

    def pwr_cb(self, win, state):
        self.yav.state = state
        return True

    def volslider_changed(self, slider):
        print(slider)
        value = slider.get_value()
        self.yav.set_volume(0, value)

    def adjust_volslider(self, yav, status):
        print('adjust_volslider', status)
        self.volSlider.set_value(value=status)
        return True

    def volbtn_click(self, widget, event, data=None):
        print(event.type, event.button)
        if event.button == 1:
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.vol_pressed = True
            elif event.type == Gdk.EventType.BUTTON_RELEASE:
                self.vol_pressed = False
            GLib.timeout_add(100, self.vol_check_loop, widget)

    def vol_check_loop(self, widget):
        if self.vol_pressed:
            slider_value = self.volSlider.get_value()
#            if -20.0 < slider_value < -70.0:
#                return False
            if widget == self.volDnBtn:
                self.yav.decrease_volume(zone=0, dec=2.0)
                self.volSlider.set_value(slider_value - 2.0)
            elif widget == self.volUpBtn:
                self.yav.increase_volume(zone=0, inc=2.0)
                self.volSlider.set_value(slider_value + 2.0)
            return True
        else:
            return False


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


class MCD(McDevice):
    def __init__(self, window, ip):
        McDevice.__init__(self, ip)
        self.window = window

    def monitor(self):
        GLib.timeout_add_seconds(4, self.checkit)

    def checkit(self):
        info = self.get_play_info()
#        print(self.get_play_info().get('artist'))
#        print(self.get_play_info().get('album'))
#        print(self.get_play_info().get('track'))
        lines = []
        lines.append(info.get('artist'))
        lines.append(info.get('album'))
        lines.append(quote(info.get('track'), safe=' '))
#        print(lines)
        for n, label in enumerate(self.window.labels):
            label.set_markup('<b><big>' + lines[n] + '</big></b>')
        return True


class YAV(YamahaAV, GObject.GObject):
    def __init__(self, window, ip):
        YamahaAV.__init__(self, ip)
#        McDevice.__init__(self, ip)
        GObject.GObject.__init__(self)
        self.window = window
        self.state = self.get_status_string('Power')
        self.prev_state = self.state
        self.powchanged_handler = self.connect('changed', window.set_power)

    def monitor(self):
        print('monitor')
        GLib.timeout_add_seconds(2, self.checkit)

    def checkit(self):
        self.state = boolit(self.get_status_string('Power'))
        if self.state != self.prev_state:
            self.emit('changed', self.state)
        volume = self.get_volume()
        print('volume in checkit    ', volume)
        if self.window.volSlider.get_value() != volume:
            print('volume at ', volume)
            self.emit('adjust', volume)
        return True

    @GObject.Signal(name='changed',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=bool,
                    arg_types=(bool,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def changed(self, state, *args):
        print(str(state) + ' hello!')
        return False

    @GObject.Signal(name='adjust',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=float,
                    arg_types=(float,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def adjust(self, volume, *args):
        print('vol_adjust')
        slider_pos = round(self.window.volSlider.get_value())
        print(slider_pos, 'slider_pos')
        print(str(volume) + ' volume!')
#        if self.window.vol_pressed:
        if volume > slider_pos:
            self.decrease_volume()
        elif volume < slider_pos:
            self.increase_volume()

        return True


def main():
    win = YamaWin()
    win.connect('destroy', Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
