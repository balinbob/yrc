#!/usr/bin/env python3

import os


class MasterZone(list):
    ''' master zone which controls all zones together '''
    cfg_file = os.path.expanduser('~/.gyrc/gyrc.cfg')
    base_port = 5030
    units = {}

    def __init__(self, mcd_list=[]):
        # Zone.__init__(self, receiver=mcd_list[0])
        list.__init__(self)
        if not mcd_list:
            from pymusiccast import McDevice
            with open(self.cfg_file, 'r') as cfg:
                ips = cfg.readlines()
            for n, ip in enumerate(ips):
                ip = ip.strip('\n')
                mcd_list.append(McDevice(ip, self.base_port+n))
        self.mcd_list = mcd_list
        for mcd in self.mcd_list:
            self.append(mcd.zones['main'])
        self.get_units()
        print('init master zone      !!')

    def set_mute(self, state):
        for zone in self:
            zone.set_mute(state)

    def set_power(self, state):
        for zone in self:
            zone.set_power(state)

    def get_power(self):
        return [z.get_status()['power'] for z in self]

    def get_mute(self):
        return [z.get_status()['mute'] for z in self]

    def get_volume(self):
        return [z.get_status()['volume'] for z in self]

    def print_status(self):
        print('power : ', self.get_power())
        print('mute  : ', self.get_mute())
        print('volume: ', self.get_volume())

    def get_max_volume(self):
        for zone in self:
            print('get max vol for: ', zone)
            print(zone.get_status()['max_volume'])

    def get_volume_for(self, n):
        return self[n].get_status()['volume']

    def get_unit_list(self):
        max_list = []
        for zone in self:
            max_list.append(zone.get_status()['max_volume'])
        mn = min(max_list)
        return [mx/mn for mx in max_list]

    def get_units(self):
        for zone in self:
            self.units.update({zone: self.get_unit_for(zone)})

    def get_unit_for(self, zone):
        return self.get_unit_list()[self.index(zone)]

    def dec_volumes(self):
        for zone in self:
            zone.set_volume(zone.get_status()['volume'] -
                            self.get_unit_for(zone))

    def inc_volumes(self):
        for zone in self:
            zone.set_volume(zone.get_status()['volume'] +
                            self.get_unit_for(zone))
