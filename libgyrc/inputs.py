#!/usr/bin/env python

# from pymusiccast import McDevice
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def get_input_list(mcd):
    features = mcd.get_features()
    input_list = features['zone'][0]['input_list']
    return input_list


class Inputs(Gtk.VBox):
    def __init__(self, mcd):
        Gtk.VBox.__init__(self)
        self.mcd = mcd
        input_list = get_input_list(mcd)
        store = Gtk.ListStore(int, str)
        for n, item in enumerate(input_list):
            store.append([n, item])
        self.cbox = Gtk.ComboBox.new_with_model(store)
        cell = Gtk.CellRendererText()
        self.cbox.pack_start(cell, True)
        self.cbox.add_attribute(cell, 'text', 1)
        self.pack_start(self.cbox, False, False, 0)
        self.select_button = Gtk.Button(label='<< Select ')
        self.cbox.connect('changed', self.on_changed, self.select_button)
        self.select_button.connect('clicked', self.on_select)
        self.select_button.set_no_show_all(True)

    def on_changed(self, combo, button, *args):
        vis = button.get_visible()
        text = self.get_active_text(combo)
        if vis and (text == self.mcd.get_status().get('input')):
            button.hide()
        elif not vis:
            button.show()

    def on_select(self, button):
        input_selected = self.get_active_text(self.cbox)
        main = self.mcd.get_zone_obj('main')
        main.set_input(input_selected)
        button.hide()

    def get_active_text(self, combo, *args):
        model = combo.get_model()
        active = combo.get_active()
        active_text = model[active][1]
        return active_text


class Win(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', Gtk.main_quit)
        self.set_default_size(300, 200)
        inputs = Inputs()
        self.add(inputs)
        self.show_all()
        Gtk.main()


if __name__ == '__main__':
    sys.exit(Win())
