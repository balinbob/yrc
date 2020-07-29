#!/usr/bin/env python3
"""Allow an application to activate a running instance of itself instead of
starting another instance.

https://gist.github.com/noamraph/8333045
"""

import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


def _get_path(app_id):
    return '/' + app_id.replace('.', '/')


def listen_for_activation(app_id, window):
    """Listen for 'activate' events. If one is sent, activate 'window'.
    """
    class MyDBUSService(dbus.service.Object):
        def __init__(self, window):
            self.window = window

            bus_name = dbus.service.BusName(app_id, bus=dbus.SessionBus())
            dbus.service.Object.__init__(self, bus_name, _get_path(app_id))

        @dbus.service.method(app_id)
        def activate(self):
            # print("The process was activated by another instance.")
            self.window.present()

    DBusGMainLoop(set_as_default=True)
    _myservice = MyDBUSService(window)


def activate_if_already_running(app_id):
    """Activate the existing window if it's already running. Return True if
    we found an existing window, and False otherwise.
    """
    bus = dbus.SessionBus()
    try:
        programinstance = bus.get_object(app_id, _get_path(app_id))
        activate = programinstance.get_dbus_method('activate', app_id)
    except dbus.exceptions.DBusException:
        return False
    else:
        # print("A running process was found. Activating it.")
        activate()
        return True
    finally:
        bus.close()
