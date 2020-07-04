#!/usr/bin/env python

import sys
# import time
from yamaha_av import YamahaAV
from pymusiccast import McDevice
import gi
from gi.repository import GObject
from gi.repository import GLib
from slider import Slider, RadioBox
from switches import RecvrPower, PPSwitch
from inputs import Inputs
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
gi.require_version('Pango', '1.0')
from gi.repository.Pango import EllipsizeMode
# ip = '192.168.1.130'


def boolit(state):
    return (True if state == 'On' else False)


class YamaWin(Gtk.Window):
    ip = '192.168.1.130'
    vol_pressed = False

    def __init__(self):

        Gtk.Window.__init__(self, title='Gyrc')
        self.connect('destroy', Gtk.main_quit)
        self.mcd = MCD(self, self.ip)
        self.yav = YAV(self, self.ip)
        self.yav.setup()
#        self.ymon = YMonitor()
#        print(self.ymon.info)
        self.recvState = self.yav.get_status_string('Power')
        self.recvPower = RecvrPower(self.yav)
        label = Gtk.Label.new_with_mnemonic('P_ower')
        label.set_mnemonic_widget(self.recvPower)
        label.set_halign(Gtk.Align.END)
        grid = Gtk.Grid()
        self.set_default_size(640, 320)
        self.add(grid)
        vspacer = Gtk.Box()
        vspacer.set_size_request(32, 32)
        grid.set_column_spacing(4)
        grid.set_row_spacing(4)
        grid.attach(label, 0, 0, 1, 1)
        hbox = Gtk.HBox()
        hbox.pack_start(self.recvPower, True, False, 32)
        grid.attach(hbox, 1, 0, 1, 1)
        self.volSlider = Slider(-80, 0.0)
        # self.volSlider.set_size_request(300, 10)
        self.volUpBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_FORWARD,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volUpBtn.set_size_request(10, 10)
        self.volDnBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_BACK,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volDnBtn.set_size_request(10, 10)
        slider_box = Gtk.HBox()
        slider_box.set_size_request(320, 10)
        slider_box.pack_start(self.volDnBtn, True, True, 0)
        slider_box.pack_start(self.volSlider, True, True, 0)
        slider_box.pack_start(self.volUpBtn, True, True, 0)

        radio_box = RadioBox(self.volSlider)

        '''
        radio_box = Gtk.HBox()
        radio_box.set_size_request(260, 15)
        radio_box.pack_start(Gtk.Label(label='max vol: '), False, False, 0)
        radio_group = []
        radio = None
        for n, val in enumerate([-30.0, -20.0, -10.0, 0.0]):
            radio = Gtk.RadioButton.new_from_widget(radio)
            radio.connect('toggled',
                          self.max_radio_toggled,
                          val,
                          self.volSlider)
            radio_group.append(radio)
            radio_box.pack_start(radio, False, False, 8)
'''

        grid.attach(slider_box, 2, 0, 15, 1)
        self.ppSwitch = PPSwitch(self.mcd)
        grid.attach(self.ppSwitch, 19, 0, 1, 1)
        label = Gtk.Label.new_with_mnemonic('_Pause/\nPlay')
        label.set_mnemonic_widget(self.ppSwitch)
        self.ppSwitch.set_active(True if self.mcd.playback == 'play'
                                 else False)
        grid.attach(label, 20, 0, 1, 1)
        grid.attach(radio_box, 8, 1, 16, 1)
        self.inputs = Inputs(self.mcd)
        self.inputs_box = self.inputs.cbox
        # self.inputs_box.connect('changed', self.on_inputs_changed)
        hbox = Gtk.HBox()
        hbox.pack_start(self.inputs, False, False, 6)
        hbox.pack_start(self.inputs.select_button, False, False, 4)
        hbox.set_size_request(320, 32)
        grid.attach(hbox, 0, 2, 20, 1)
        self.info_box = Gtk.VBox()
        self.info_box.set_size_request(10, 10)
        self.labels = []
        for n in range(3):
            self.labels.append(Gtk.Label())
            self.labels[n].set_max_width_chars(65)
            self.labels[n].set_halign(Gtk.Align.START)
            self.labels[n].set_ellipsize(EllipsizeMode.END)
            hbox = Gtk.HBox()
            hbox.pack_start(self.labels[n], True, True, 4)
            self.info_box.pack_start(hbox, True, False, 8)

#        self.mcd.checkit()
        grid.attach(self.info_box, 1, 3, 28, 1)
        print('---')
        self.volSlider.set_value(self.yav.get_volume())
        self.recvPower.set_state(boolit(self.recvState))
        self.yav.monitor()
        self.mcd.monitor()
        self.yav.connect('changed', self.set_power)
        self.mcd.connect('play-toggled',
                         self.on_play_toggled,
                         self.mcd.playback)
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

        self.volUpBtn.connect_object('clicked', self.vol_up, self.volSlider)
        self.volDnBtn.connect_object('clicked', self.vol_down, self.volSlider)

        self.show_all()

#        thread = threading.Thread(target=self.ymon.run)
#        thread.daemon = True
#        thread.start()

    '''
    def max_radio_toggled(self, radio, float, slider, *args):
        if radio.get_active():
            print(float)
            print(slider)
            slider.set_fill_level(float)
'''

    def on_play_toggled(self, mcd, status=None, *args):
        #        print('        play_toggled')
        #   print('status:  %s' % status)
        # print(args[0])
        self.ppSwitch.set_active(
            True if status == 'play' else False)

    def on_inputs_changed(self, input_box):
        model = input_box.get_model()
        active = input_box.get_active()
        service = model[active][1]
        print(service)
        # self.mcd.zone()
        main = self.mcd.get_zone_obj('main')
        main.set_input(service)

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
        # print(slider)
        value = slider.get_value()
        self.yav.set_volume(0, value)

    def adjust_volslider(self, yav, status):
        # print('adjust_volslider', status)
        self.volSlider.set_value(value=status)
        return True

    def volbtn_click(self, widget, event, data=None):
        #        print(event.type, event.button)
        if event.button == 1:
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.vol_pressed = True
            elif event.type == Gdk.EventType.BUTTON_RELEASE:
                self.vol_pressed = False
            GLib.timeout_add(200, self.vol_check_loop, widget)

    def vol_check_loop(self, widget):
        if self.vol_pressed:
            slider_value = self.volSlider.get_value()
            if widget == self.volDnBtn:
                self.yav.decrease_volume(zone=0, dec=2.0)
                self.volSlider.set_value(slider_value - 2.0)
            elif widget == self.volUpBtn:
                self.yav.increase_volume(zone=0, inc=2.0)
                self.volSlider.set_value(slider_value + 2.0)
            return True
        else:
            return False


class YMonitor(McDevice):
    def __init__(self, host='yamaha', port=5007):
        McDevice.__init__(self, host, port)
        self.new_info = self.get_play_info()
        self.info = self.new_info
        self.main_zone = self.zones.get('main')
        self.handle_status()

    def run(self):
        while True:
            self.msg = self.messages.get()

            if b'netusb' in self.msg:

                self.new_info = self.get_play_info()
                if self.new_info != self.info:
                    for item in self.new_info:
                        if 'time' in item:
                            continue
                        value = self.new_info.get(item)
                        if value != self.info.get(item):
                            print('%s:  %s' % (item, value))
                    self.info = self.new_info

            if b'zone' in self.msg:
                print('                        zone')
                print(self.main_zone.get_status())

        return False


class MCD(McDevice, GObject.GObject):
    def __init__(self, window, ip):
        McDevice.__init__(self, ip)
        GObject.GObject.__init__(self)
        self.window = window
        info = self.get_play_info()
        self.playback = info.get('playback')
        self.prev_playback = self.playback

    def monitor(self):
        GLib.timeout_add_seconds(1, self.checkit)

    def checkit(self):
        info = self.get_play_info()
        lines = []
        lines.append(info.get('artist'))
        lines.append(info.get('album'))
        lines.append(info.get('track'))
        if info.get('playback') != self.prev_playback:
            self.playback = info.get('playback')
            self.prev_playback = self.playback
            self.emit('play-toggled', self.playback)

        for n, label in enumerate(self.window.labels):
            lines[n] = lines[n].replace('&', '&amp;')
            label.set_markup('<b><big>' + lines[n] + '</big></b>')
        return True

    @GObject.Signal(name='play_toggled',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=str,
                    arg_types=(str,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def play_toggled(self, state, *args):
        # print('Helloooooooooooo!')
        return False

    def get_zones(self):
        zones = self.get_features()['zone']
        for zone in zones:
            print(zone['id'])

    def zone(self, zone='main'):
        print(self.get_features()['zone'][0])
        print('')
        self.get_zones()

    def get_zone_obj(self, zone='main'):
        return self.zones[zone]


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
        GLib.timeout_add_seconds(1, self.checkit)

    def checkit(self):
        self.state = boolit(self.get_status_string('Power'))
        if self.state != self.prev_state:
            self.emit('changed', self.state)
        volume = self.get_volume()
        if self.window.volSlider.get_value() != volume:
            self.emit('adjust', volume)
        return True

    @GObject.Signal(name='changed',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=bool,
                    arg_types=(bool,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def changed(self, state, *args):
        return False

    @GObject.Signal(name='adjust',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=float,
                    arg_types=(float,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def adjust(self, volume, *args):
        slider_pos = round(self.window.volSlider.get_value())
        if volume > slider_pos:
            self.decrease_volume()
        elif volume < slider_pos:
            self.increase_volume()

        return True


def main():
    YamaWin()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
