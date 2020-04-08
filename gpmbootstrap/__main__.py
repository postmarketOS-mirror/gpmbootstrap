import os
import threading

import gi
import logging

from gpmbootstrap import devicefinder

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject, Gio, GdkPixbuf

gi.require_version('Handy', '0.0')
from gi.repository import Handy

import gpmbootstrap.pmos as pmos

logging.basicConfig(level=logging.DEBUG)


class Installer(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback

        self.codename = None
        self.hostname = None
        self.ssh = None
        self.timezone = None
        self.ui = None
        self.user = None
        self.password = None
        self.packages = None
        self.sdcard = None

    def run(self):
        GLib.idle_add(self.callback, 0, "Starting pmbootstrap")
        pmos.config(
            codename=self.codename,
            hostname=self.hostname,
            ssh=self.ssh,
            timezone=self.timezone,
            ui=self.ui,
            user=self.user
        )
        GLib.idle_add(self.callback, 0.1, "Building rootfs")
        pmos.install(
            password=self.password,
            packages=self.packages,
            sdcard=self.sdcard
        )
        GLib.idle_add(self.callback, 1, "Install complete!")


class InstallerApplication(Gtk.Application):
    def __init__(self, application_id, flags):
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)

    def new_window(self, *args):
        AppWindow(self)


class AppWindow:
    def __init__(self, application):
        self.application = application
        builder = Gtk.Builder()
        builder.add_from_resource('/org/postmarketos/gpmbootstrap/ui/main.ui')
        builder.connect_signals(self)

        css = Gio.resources_lookup_data("/org/postmarketos/gpmbootstrap/ui/style.css", 0)

        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(css.get_data())

        window = builder.get_object("main_window")

        self.main_stack = builder.get_object("main_stack")
        self.page_flasher = builder.get_object("page_flasher")

        self.device = builder.get_object("device")
        self.manufacturer = builder.get_object("manufacturer")
        self.ui = builder.get_object("ui")
        self.username = builder.get_object("username")
        self.password = builder.get_object("password")
        self.hostname = builder.get_object("hostname")
        self.timezone = builder.get_object("timezone")
        self.ssh = builder.get_object("ssh")
        self.packages = builder.get_object("packages")

        self.sdcard = builder.get_object("sdcard")

        self.progress = builder.get_object("progress")
        self.log = builder.get_object("log")

        window.set_application(self.application)

        self.apply_css(window, self.provider)

        self.populate_devices()
        self.populate_uis()
        self.populate_timezones()

        window.show_all()

        Gtk.main()

    def apply_css(self, widget, provider):
        Gtk.StyleContext.add_provider(widget.get_style_context(),
                                      provider,
                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        if isinstance(widget, Gtk.Container):
            widget.forall(self.apply_css, provider)

    def populate_devices(self):
        for item in pmos.get_vendors():
            self.manufacturer.append_text(item)

    def populate_uis(self):
        for name, desc in pmos.get_user_interfaces():
            self.ui.append_text(name)
        self.ui.set_active(0)

    def populate_timezones(self):
        timezones = pmos.get_timezones()
        for zone in timezones:
            self.timezone.append_text(zone)
        self.timezone.set_active(timezones.index("GMT"))

    def on_manufacturer_changed(self, widget, *args):
        active = widget.get_active_text()
        codenames = pmos.get_codenames(active)
        self.device.remove_all()
        for cn in codenames:
            self.device.append_text(cn)
        self.device.set_sensitive(active is not None)

    def on_device_changed(self, widget, *args):
        active = widget.get_active_text()
        if active:
            self.hostname.set_text(active)

            info = pmos.get_device_info(active)
            methods = []
            if info["flash_method"] == 'none':
                if info["external_storage"] == 'true':
                    methods.append("sdcard")
                else:
                    methods.append("zip")
            else:
                methods.append(info["flash_method"])
                methods.append("zip")

            if "sdcard" in methods:
                cards = devicefinder.find_sdcard()
                self.sdcard.remove_all()
                for card in cards:
                    self.sdcard.append_text("{} {}".format(*card))
                if len(cards) > 0:
                    self.sdcard.set_active(0)

    def on_start_clicked(self, button, *args):
        button.set_sensitive(False)
        self.main_stack.set_visible_child(self.page_flasher)
        thread = Installer(self.on_progress)
        thread.codename = self.device.get_active_text()
        thread.timezone = self.timezone.get_active_text()
        thread.user = self.username.get_text()
        thread.hostname = self.hostname.get_text()
        thread.ssh = self.ssh.get_active()
        thread.ui = self.ui.get_active_text()
        thread.password = self.password.get_text()
        thread.packages = self.packages.get_text().replace(",", " ").split(" ")
        thread.sdcard = self.sdcard.get_active_text().split(" ")[0]
        thread.start()

    def on_progress(self, value, status):
        self.progress.set_fraction(value)
        self.progress.set_text(status)


def main():
    # This is to make the Handy module actually loaded to be used in the GtkBuilder
    Handy.Column()
    pmos.init()

    if os.path.isfile('gpmbootstrap.gresource'):
        print("Using resources from cwd")
        resource = Gio.resource_load("gpmbootstrap.gresource")
        Gio.Resource._register(resource)
    else:
        print("Using resources from pkg_resources")
        with pkg_resources.path('gpmbootstrap', 'gpmbootstrap.gresource') as resource_file:
            resource = Gio.resource_load(str(resource_file))
            Gio.Resource._register(resource)

    app = InstallerApplication("org.postmarketos.gpmbootstrap", Gio.ApplicationFlags.FLAGS_NONE)
    app.run()


if __name__ == '__main__':
    main()
