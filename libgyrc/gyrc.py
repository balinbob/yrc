#!/usr/bin/env python3

import sys
import gi
from gi.repository import GLib
# from .mcd import MCD
from .ifrunning import listen_for_activation, activate_if_already_running
from .mcd import DeviceList
# from .radiobox import RadioBox
from .switches import RecvrPower
from .inputs import Inputs
from .cover import Cover, get_artwork
from .master import Master
from .devicebox import DeviceBox, Expander
# from .config import Config
from .playerbuttons import PlayerButtons
from importlib import import_module

gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
Gtk = import_module('gi.repository.Gtk')
Gdk = import_module('gi.repository.Gdk')
Pango = import_module('gi.repository.Pango')
EllipsizeMode = Pango.EllipsizeMode


def db2vol(db):
    return 161+(db * 2)


class YamaWin(Gtk.Window):
    ip_address = None
    vol_pressed = False
    ips = []
    # mcd_list = DeviceList()

    def __init__(self):
        Gtk.Window.__init__(self, title='Gyrc')
        self.connect('destroy', Gtk.main_quit)
        self.mcd_list = DeviceList(self)
        self.zone_list = []

        for n, mcdevice in enumerate(self.mcd_list):
            print('connected to %s' % mcdevice.name)

        self.zone_list = self.mcd_list.get_zone_list()

        for n, zone in enumerate(self.zone_list):
            pass

        self.devBox = DeviceBox(self.mcd_list)
        self.expander = Expander(self.devBox)
        self.expander.add(self.devBox)

        try:
            self.mcd = self.mcd_list[0]     # stub
        except IndexError:
            print('ip address(es) not configured')
            sys.exit(2)
        self.recvState = self.mcd.get_power_state()
        self.recvPower = RecvrPower(self.mcd)
        label = Gtk.Label.new_with_mnemonic('P_ower')
        label.set_mnemonic_widget(self.recvPower)
        label.set_halign(Gtk.Align.END)
        grid = Gtk.Grid()
        self.set_default_size(340, 320)
        self.add(grid)
        vspacer = Gtk.Box()
        vspacer.set_size_request(32, 32)
        grid.set_column_spacing(4)
        grid.set_row_spacing(4)
        self.master = Master(self.mcd_list)
        self.sliderbox = self.master.sliderbox
        self.volSlider = self.sliderbox.slider
        self.volUpBtn = self.sliderbox.volUpBtn
        self.volDnBtn = self.sliderbox.volDnBtn
        # self.radio_box = self.master.radiobox

        self.inputs = Inputs(self.mcd)
        self.inputs_box = self.inputs.cbox
        # self.radio_box = RadioBox(self.volSlider)
        self.row2 = Gtk.HBox()
        hbox1 = Gtk.HBox()
        # vbox2 = Gtk.VBox()
        hbox1.set_size_request(330, 10)
        # vbox2.set_size_request(200, 10)
        hbox1.pack_start(self.inputs, False, False, 2)
        hbox1.pack_start(self.inputs.select_button, False, False, 2)
        # vbox2.pack_start(self.radio_box, False, False, 2)
        # self.row2.pack_start(hbox1, False, False, 2)
        # self.row2.pack_start(vbox2, False, False, 2)
        self.row2.pack_start(self.master, False, False, 2)
        grid.attach(hbox1, 0, 2, 1, 1)
        grid.attach(self.row2, 4, 2, 10, 1)

        self.info_box = Gtk.VBox()
        self.info_box.set_size_request(10, 10)
        self.labels = []
        for n in range(4):
            self.labels.append(Gtk.Label())
            self.labels[n].set_max_width_chars(72)
            self.labels[n].set_halign(Gtk.Align.START)
            self.labels[n].set_ellipsize(EllipsizeMode.END)
            hbox = Gtk.HBox()
            hbox.pack_start(self.labels[n], False, False, 4)
            self.info_box.pack_start(hbox, False, False, 6)

        self.cover = Cover(self.mcd)
        self.bbox = PlayerButtons(self.mcd)
        self.bbox.set_size_request(20, 20)

        grid.attach(self.cover, 0, 4, 4, 2)
        grid.attach(self.bbox, 4, 4, 3, 1)
        grid.attach(self.info_box, 4, 5, 18, 1)

        grid.attach(self.expander, 0, 7, 22, 1)

        self.grid = grid

        # self.volSlider.set_value(self.mcd.get_volume_db())
        # self.set_volume_limit()
        self.mcd.monitor()
        self.mcd.connect('changed', self.set_power)
        self.mcd.connect('artwork-changed',
                         self.on_artwork_changed)
        # self.recvPower.connect('state-set', self.pwr_cb)

        # self.volhandler = self.volSlider.connect('value-changed',
        #                                          self.volslider_changed)
        self.volslider_id = self.mcd.connect('adjust',
                                             self.adjust_volslider)
        self.volUpBtn.connect('button-press-event', self.volbtn_click)
        self.volUpBtn.connect('button-release-event', self.volbtn_click)
        self.volDnBtn.connect('button-press-event', self.volbtn_click)
        self.volDnBtn.connect('button-release-event', self.volbtn_click)

        self.volUpBtn.connect_object('clicked', self.vol_up, self.volSlider)
        self.volDnBtn.connect_object('clicked', self.vol_down, self.volSlider)
        self.recvPower.set_active(self.recvState)
        self.show_all()
        self.set_title('Gyrc - ' +
                       self.mcd.get_device_info().get('model_name'))
    '''
    def set_volume_limit(self):
        volume_limit = self.radio_box.get_volume_limit()
        for mcd in self.mcd_list:
            # print('volume_limit: ', volume_limit)
            mcd.set_volume_limit(volume_limit)
    '''
    def on_artwork_changed(self, mcd, *args):
        pixbuf = get_artwork(mcd)
        self.cover.cover.set_from_pixbuf(pixbuf)

    def on_inputs_changed(self, input_box):
        model = input_box.get_model()
        active = input_box.get_active()
        service = model[active][1]
        # print(service)
        main = self.mcd.get_zone_obj('main')
        main.set_input(service)

    def vol_up(self, volslider):
        value = volslider.get_value()

        print('vol_up: ', value)

        volslider.set_value(value + 0.5)
        self.mcd.increase_volume(0.5)

    def vol_down(self, volslider):
        value = volslider.get_value()
        volslider.set_value(value - 0.5)
        self.mcd.decrease_volume(0.5)

    def set_power(self, mcd, status, *args):
        self.recvState = status
        self.recvPower.set_state(self.recvState)
        return True

    def pwr_cb(self, win, state):
        self.mcd.state = state
        return True

    def volslider_changed(self, slider):
        db = slider.get_value()
        self.mcd.set_volume(db2vol(db))

    def adjust_volslider(self, mcd, status):
        # active_limit = self.radio_box.get_radio_value()
        self.volSlider.set_value(value=status)
        return True

    def volbtn_click(self, widget, event, data=None):
        if event.button == 1:
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.vol_pressed = True
            elif event.type == Gdk.EventType.BUTTON_RELEASE:
                self.vol_pressed = False
            GLib.timeout_add(200, self.vol_check_loop, widget)

    def vol_check_loop(self, widget):
        if self.vol_pressed:
            slider_value = self.volSlider.get_value()

            # print(slider_value, ' is slider value')

            if widget == self.volDnBtn:
                self.mcd.decrease_volume(2.0)
                self.volSlider.set_value(slider_value - 2.0)
            elif widget == self.volUpBtn:
                self.mcd.increase_volume(2.0)
                self.volSlider.set_value(slider_value + 2.0)
            return True
        else:
            return False


def main():
    APP_ID = 'com.balinbob.gyrc'
    activated = activate_if_already_running(APP_ID)
    if activated:
        sys.exit(0)

    win = YamaWin()

    listen_for_activation(APP_ID, win)
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
