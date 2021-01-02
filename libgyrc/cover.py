#!/usr/bin/env python

import sys
import requests
import gi
from importlib import import_module
from pymusiccast import McDevice
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')
GdkPixbuf = import_module('gi.repository.GdkPixbuf')


def get_artwork(mcd):
    url = 'http://' + \
            mcd.ip_address + \
            mcd.get_play_info().get('albumart_url')
    r = requests.get(url)
    with open('/tmp/cover.jpg', 'wb') as f:
        f.write(r.content)
        r.close()
    pixbuf = None
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename='/tmp/cover.jpg',
                    width=300,
                    height=300,
                    preserve_aspect_ratio=True)
    except Exception as e:
        print(e)
    return pixbuf


class Cover(Gtk.VBox):
    def __init__(self, mcd):
        Gtk.VBox.__init__(self)
        self.cover = Gtk.Image()
        self.pixbuf = get_artwork(mcd)
        self.cover.set_from_pixbuf(self.pixbuf)
        self.set_size_request(20, 20)
        self.add(self.cover)


def main():
    mcd = McDevice('yamaha', 5007)
#    url = 'http://' + mcd.ip_address + mcd.get_play_info().get('albumart_url')
#    print(url)
    cover = Cover(mcd)
    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    win.add(cover)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
