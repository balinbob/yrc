#!/usr/bin/env python

import sys
# import time
# from yamaha_av import YamahaAV
from pymusiccast import McDevice
import gi
from gi.repository import GObject
from gi.repository import GLib
from slider import Slider, RadioBox
from switches import RecvrPower, PPSwitch
from inputs import Inputs
from cover import Cover, get_artwork
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
gi.require_version('Pango', '1.0')
from gi.repository.Pango import EllipsizeMode
# ip = '192.168.1.130'


def boolit(state):
    return (True if state == 'on' else False)


def format_time(seconds):
    min = int(seconds/60)
    sec = seconds - (min * 60)
    return ('%02d:%02d' % (min, sec))


def db2vol(db):
    return 161+(db * 2)


class YamaWin(Gtk.Window):
    ip = '192.168.1.130'
    vol_pressed = False

    def __init__(self):

        Gtk.Window.__init__(self, title='Gyrc')
        self.connect('destroy', Gtk.main_quit)
        self.mcd = MCD(self, self.ip)
#        self.ymon = YMonitor()
#        print(self.ymon.info)
        self.recvState = self.mcd.get_power_state()
        self.recvPower = RecvrPower(self.mcd)
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
        self.volUpBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_FORWARD,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volUpBtn.set_size_request(10, 10)
        self.volDnBtn = Gtk.Button.new_from_icon_name(
                        Gtk.STOCK_GO_BACK,
                        Gtk.IconSize.SMALL_TOOLBAR)
        self.volDnBtn.set_size_request(10, 10)
        slider_box = Gtk.HBox()
        slider_box.set_size_request(300, 10)
        slider_box.pack_start(self.volDnBtn, True, True, 0)
        slider_box.pack_start(self.volSlider, True, True, 0)
        slider_box.pack_start(self.volUpBtn, True, True, 0)

        self.radio_box = RadioBox(self.volSlider)
        grid.attach(slider_box, 2, 0, 15, 1)
        self.ppSwitch = PPSwitch(self.mcd)
        grid.attach(self.ppSwitch, 19, 0, 1, 1)
        label = Gtk.Label.new_with_mnemonic('_Pause/\nPlay')
        label.set_mnemonic_widget(self.ppSwitch)
        self.ppSwitch.set_active(True if self.mcd.playback == 'play'
                                 else False)
        grid.attach(label, 20, 0, 1, 1)
        grid.attach(self.radio_box, 8, 1, 14, 1)
        self.inputs = Inputs(self.mcd)
        self.inputs_box = self.inputs.cbox
        # self.inputs_box.connect('changed', self.on_inputs_changed)
        hbox = Gtk.HBox()
        hbox.pack_start(self.inputs, False, False, 6)
        hbox.pack_start(self.inputs.select_button, False, False, 4)
        hbox.set_size_request(160, 32)
        grid.attach(hbox, 0, 2, 12, 1)
        self.info_box = Gtk.VBox()
        self.info_box.set_size_request(10, 10)
        self.labels = []
        for n in range(4):
            self.labels.append(Gtk.Label())
            self.labels[n].set_max_width_chars(65)
            self.labels[n].set_halign(Gtk.Align.START)
            self.labels[n].set_ellipsize(EllipsizeMode.END)
            hbox = Gtk.HBox()
            hbox.pack_start(self.labels[n], True, True, 4)
            self.info_box.pack_start(hbox, True, False, 8)

        self.cover = Cover(self.mcd)
        spacer = Gtk.VBox()
        spacer.set_size_request(20, 100)
        grid.attach(self.cover, 0, 3, 8, 2)
        grid.attach(spacer, 10, 3, 20, 1)
        grid.attach(self.info_box, 9, 4, 20, 1)
        self.grid = grid
        print('---')
        self.volSlider.set_value(self.mcd.get_volume_db())
        self.mcd.monitor()
        self.mcd.connect('changed', self.set_power)
        self.mcd.connect('play-toggled',
                         self.on_play_toggled,
                         self.mcd.playback)
        self.mcd.connect('artwork-changed',
                         self.on_artwork_changed)
        self.recvPower.connect('state-set', self.pwr_cb)
        self.volhandler = self.volSlider.connect('value-changed',
                                                 self.volslider_changed)
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

#        thread = threading.Thread(target=self.ymon.run)
#        thread.daemon = True
#        thread.start()

    def on_artwork_changed(self, mcd, *args):
        pixbuf = get_artwork(mcd)
        self.cover.cover.set_from_pixbuf(pixbuf)

    def on_play_toggled(self, mcd, status=None, *args):
        self.ppSwitch.set_active(
            True if status == 'play' else False)

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
        print('slider at ', db, ' in volslider_changed')
        self.mcd.set_volume(db2vol(db))

    def adjust_volslider(self, mcd, status):
        active_limit = self.radio_box.get_radio_value()
        print('active_limit is ', active_limit)
        print('adjust_volslider ', status)

#        if status < self.radio_box.active_limit:
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

            print(slider_value, ' is slider value')

            if widget == self.volDnBtn:
                self.mcd.decrease_volume(2.0)
                self.volSlider.set_value(slider_value - 2.0)
            elif widget == self.volUpBtn:
                self.mcd.increase_volume(2.0)
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
        # self.handle_status()

    def run(self):
        while True:
            self.msg = self.messages.get()

            if b'netusb' in self.msg:

                self.new_info = self.get_play_info()
                if self.new_info != self.info:
                    for item in self.new_info:
                        if 'time' in item:
                            continue
                        # value = self.new_info.get(item)
                        # if value != self.info.get(item):
                            # print('%s:  %s' % (item, value))
                    self.info = self.new_info

            if b'zone' in self.msg:
                print('                        zone')
                # print(self.main_zone.get_status())

        return False


class MCD(McDevice, GObject.GObject):
    def __init__(self, window, ip):
        McDevice.__init__(self, ip)
        GObject.GObject.__init__(self)
        self.window = window
        info = self.get_play_info()
        self.playback = info.get('playback')
        self.prev_playback = self.playback
        self.art_url = ''
        self.power_state = boolit(self.get_status().get('power'))
        self.volume = self.get_volume()
        print(self.volume)

        self.zone_obj = self.get_zone_obj()

    def get_volume_db(self):
        ''' return current volume in db '''
        status = self.get_status()
        return status.get('actual_volume').get('value')

    def get_volume(self):
        ''' return current volume in range 0-161 '''
        status = self.get_status()
        return status.get('volume')

    def get_power_state(self):
        status = self.get_status()
        return boolit(status.get('power'))

    def set_power_state(self, state):
        self.zone_obj.set_power(state)

    def monitor(self):
        GLib.timeout_add_seconds(1, self.checkit)

    def checkit(self):
        info = self.get_play_info()
        lines = []
        lines.append(info.get('artist'))
        lines.append(info.get('album'))
        lines.append(info.get('track'))
        play_time = info.get('play_time')
        if play_time:
            play_time = format_time(play_time)
            lines.append('play time:  %s' % str(play_time))
        if info.get('playback') != self.prev_playback:
            self.playback = info.get('playback')
            self.prev_playback = self.playback
            self.emit('play-toggled', self.playback)

        if info.get('albumart_url') != self.art_url:
            self.art_url = info.get('albumart_url')
            self.emit('artwork-changed', '')

        if self.power_state != self.get_power_state():
            self.power_state = self.get_power_state()
            self.emit('changed', self.power_state)
        volume = self.get_volume_db()
        if self.window.volSlider.get_value() != volume:
            self.emit('adjust', volume)

        for n, label in enumerate(self.window.labels):
            try:
                lines[n] = lines[n].replace('&', '&amp;')
                label.set_markup('<b><big>' + lines[n] + '</big></b>')
            except IndexError:
                pass
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

    @GObject.Signal(name='play_toggled',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=str,
                    arg_types=(str,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def play_toggled(self, state, *args):
        # print('Helloooooooooooo!')
        return False

    @GObject.Signal(name='artwork-changed',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=str,
                    arg_types=(str,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def artwork_changed(self, state, *args):
        # print('Helloooooooooooo!')
        return False

    def decrease_volume(self, dec=0.5):
        volume = self.get_volume()
        print('mcd._decrease_volume volume is ', volume)
        self.zone_obj.set_volume(volume + db2vol(dec))

    def increase_volume(self, inc=0.5):
        print('mcd.increase_vol')
        volume = self.get_volume()
        self.zone_obj.set_volume(volume - db2vol(inc))

    def set_volume_db(self, db):
        print('set_volume_db')
        self.zone_obj.set_volume(db2vol(db))

    def set_volume(self, volume):
        print('set_volume ', volume)
        self.zone_obj.set_volume(volume)

    def get_zones(self):
        zones = self.get_features()['zone']
        for zone in zones:
            print(zone['id'])

    def zone(self, zone='main'):
        # print(self.get_features()['zone'][0])
        # print('')
        self.get_zones()

    def get_zone_obj(self, zone='main'):
        return self.zones[zone]


'''
class YAV(YamahaAV, GObject.GObject):
    def __init__(self, window, ip):
        YamahaAV.__init__(self, ip)
        GObject.GObject.__init__(self)
        self.window = window
        self.state = self.get_status_string('Power')
        self.prev_state = self.state
        self.powchanged_handler = self.connect('changed', window.set_power)

    def monitor(self):
        # print('monitor')
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
'''


def main():
    YamaWin()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
