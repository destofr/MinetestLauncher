import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from pkg_resources import resource_string
import requests

from . import APP_ID, VERSION


def main():
    app = Gtk.Application(application_id=APP_ID)
    app.connect("activate", LauncherWindow)
    app.run(None)


def template(c):
    return Gtk.Template(string=resource_string(__name__, c.__gtype_name__ + ".ui"))(c)


@template
class ServerWidget(Gtk.Box):
    __gtype_name__ = "ServerWidget"
    server_name = Gtk.Template.Child("server_name")

    def __init__(self, server):
        super().__init__()
        self.server_name.set_label(server["name"])


@template
class ServerList(Gtk.Box):
    __gtype_name__ = "ServerList"

    def __init__(self):
        super().__init__()

    def populate(self, servers):
        for server in servers:
            self.append(ServerWidget(server))


@template
class LauncherWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "LauncherWindow"
    server_list = Gtk.Template.Child("server_list")

    def __init__(self, app):
        super().__init__(application=app)
        servers = requests.get("https://servers.minetest.net/list").json()["list"]
        self.server_list.populate(servers)
        self.present()


if __name__ == "__main__":
    main()
