#!/usr/bin/env python3

import sys
import os
from pymusiccast import McDevice
from pymusiccast.exceptions import YMCInitError
from json.decoder import JSONDecodeError
from .config import Config

from gi.repository import GObject
from gi.repository import GLib


def boolit(state):
    return (True if state == 'on' else False)


def format_time(seconds):
    min = int(seconds/60)
    sec = seconds - (min * 60)
    return ('%02d:%02d' % (min, sec))


cfg_name = os.path.expanduser('~/.gyrc/gyrc.cfg')
ip_list = []


class DeviceList(list):
    zone_list = []

    def __init__(self, window):
        list.__init__(self)
        config = Config()
        ip_list = config.get_config()

        for ip in ip_list:
            ip = ip.strip('\n')
            mcd = MCD(window, ip)
            self.add(mcd)

    def add(self, mcd):
        self.append(mcd)

    def devices_get(self):
        return self

    def get_n_devices(self):
        return len(self)

    def get_device(self, n=0):
        try:
            return self[n]
        except IndexError:
            return None

    def get_name_for_device(self, n=0):
        return self[n].name

    def get_power_for_device(self, n=0):
        return self[n].get_status()['power']

    def get_volume_for_device(self, n=0):
        return self[n].get_status()['volume']

    def get_max_volume_for_device(self, n=0):
        return self[n].get_status()['max_volume']

    def get_zone_for_device(self, n=0):
        return self[n].zones['main']

    def get_zone_list(self):
        for n, device in enumerate(self):
            self.zone_list.append(device.zones['main'])
        return self.zone_list


class MCD(McDevice, GObject.GObject):
    # mcd_list = DeviceList()
    volume_limit = 0

    def __init__(self, window, ip, udp_port=None):
        for udp_port in range(5010, 5019):
            try:
                print('trying port %d' % udp_port)
                McDevice.__init__(self, ip, udp_port)
                print('Got It!')

                break
            except YMCInitError as e:
                if udp_port == 5019:
                    print('cannot establish connection to %s' % ip)
                    print(e)
                    sys.exit(255)
            except JSONDecodeError:
                print('device does not respond..')
                sys.exit(255)

        GObject.GObject.__init__(self)
        self.window = window
        info = self.get_play_info()
        self.playback = info.get('playback')
        self.prev_playback = self.playback
        self.emit('playback-changed', self.playback)
        self.art_url = ''
        self.power_state = boolit(self.get_status().get('power'))
        self.volume = self.get_volume()
        self.max_volume = self.get_max_volume()
        self.zone_obj = self.get_zone_obj()

    def set_volume_limit(self, limit):
        # print('in mcd:     ', limit)
        self.volume_limit = limit

    def db2vol(self, db):
        return self.max_volume+(db * 2)

    def set_window(self, window):
        self.window = window

    # def get_device_list(self):
    #    return self.mcd_list

    def get_max_volume(self):
        status = self.get_status()
        return status.get('max_volume')

    def get_volume_db(self):
        ''' return current volume in db '''
        status = self.get_status()
        return status.get('actual_volume').get('value')

    def get_volume(self):
        ''' return current volume in range 0-161 (or max_volume) '''
        status = self.get_status()
        return status.get('volume')

    def increment_volume(self):
        volume = self.zone_obj.get_status()['volume']
        self.zone_obj.set_volume(volume+1)
        return self.zone_obj.get_status()['volume']

    def get_power_state(self):
        status = self.get_status()
        return boolit(status.get('power'))

    def set_power_state(self, state):
        self.zone_obj.set_power(state)

    def monitor(self):
        GLib.timeout_add_seconds(1, self.checkit)

    def checkit(self):
        # self.window.set_volume_limit()
        # print('volume limit in mcd: ', self.volume_limit)
        info = self.get_play_info()
        lines = []
        lines.append(info.get('artist'))
        lines.append(info.get('album'))
        lines.append(info.get('track'))
        total_time = info.get('total_time')
        play_time = info.get('play_time')
        if total_time or (play_time > 0):
            play_time = format_time(play_time)
            total_time = format_time(total_time)
            lines.append('play time:  %s / %s' %
                         (str(play_time), str(total_time)))

        if info.get('playback') != self.prev_playback:
            self.playback = info.get('playback')
            self.prev_playback = self.playback
            self.emit('playback-changed', self.playback)

        if info.get('albumart_url') != self.art_url:
            self.art_url = info.get('albumart_url')
            self.emit('artwork-changed', '')

        if self.power_state != self.get_power_state():
            self.power_state = self.get_power_state()
            self.emit('changed', self.power_state)
        # volume = self.get_volume_db()
        # if self.window.volSlider.get_value() != volume:
        #     self.emit('adjust', volume)

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

    @GObject.Signal(name='playback-changed',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=str,
                    arg_types=(str,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def play_toggled(self, state, *args):
        return False

    @GObject.Signal(name='artwork-changed',
                    flags=GObject.SignalFlags.RUN_LAST,
                    return_type=str,
                    arg_types=(str,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def artwork_changed(self, state, *args):
        return False

    def decrease_volume(self, dec=0.5):
        volume = self.get_volume()
        print('mcd.decrease_volume volume is ', volume)
        self.zone_obj.set_volume(volume + self.db2vol(dec))

    def increase_volume(self, inc=0.5):
        print('mcd.increase_vol')
        volume = self.get_volume()
        self.zone_obj.set_volume(volume - self.db2vol(inc))

    '''def set_volume_db(self, db):
        # print('set_volume_db')
        self.zone_obj.set_volume(db2vol(db))
'''

    def set_volume(self, volume):
        print('set_volume ', volume)
        self.zone_obj.set_volume(volume)

    def get_zones(self):
        zones = self.get_features()['zone']
        for zone in zones:
            print(zone['id'])

    def zone(self, zone='main'):
        self.get_zones()

    def get_zone_obj(self, zone='main'):
        return self.zones[zone]
