import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from pkg_resources import resource_string
from pathlib import Path
import requests
import configparser
import subprocess

from . import APP_ID, VERSION


def main():
    global passwords
    passwords = LoginManager(
        Path(GLib.get_user_config_dir()) / APP_ID / "passwords.cfg"
    )
    print(passwords.path)

    app = Gtk.Application(application_id=APP_ID)
    app.connect("activate", LauncherWindow)
    app.run(None)


def launch(address, port):
    if address not in passwords:
        raise NotImplementedError("Cannot add passwords")
    else:
        login = passwords[address]
        subprocess.run(
            (
                "flatpak",
                "run",
                "net.minetest.Minetest",
                "--go",
                "--address",
                address,
                "--port",
                str(port),
                "--name",
                login["username"],
                "--password",
                login["password"],
            )
        )


def template(c):
    return Gtk.Template(string=resource_string(__name__, c.__gtype_name__ + ".ui"))(c)


class LoginManager(configparser.ConfigParser):
    def __init__(self, path):
        super().__init__()
        self.path = Path(path)
        if self.path.exists():
            self.read(self.path)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        with temp.open("w") as f:
            self.write(f)
        temp.replace(self.path)


@template
class ServerWidget(Gtk.Box):
    __gtype_name__ = "ServerWidget"
    server_name = Gtk.Template.Child("server_name")
    address = Gtk.Template.Child("address")
    run_button = Gtk.Template.Child("run_button")

    def __init__(self, server):
        super().__init__()
        self.data = server
        self.server_name.set_label(server["name"])
        self.address.set_label(f'{server["address"]}:{server["port"]}')
        self.run_button.connect(
            "clicked", lambda _w: launch(self.data["address"], self.data["port"])
        )


@template
class ServerList(Gtk.Box):
    __gtype_name__ = "ServerList"

    def __init__(self):
        super().__init__()
        self.add_css_class("ServerList")

    def populate(self, servers):
        for server in servers:
            self.append(ServerWidget(server))


@template
class LauncherWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "LauncherWindow"
    server_list = Gtk.Template.Child("server_list")

    def __init__(self, app):
        super().__init__(application=app)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(resource_string(__name__, "main.css"))
        Gtk.StyleContext().add_provider_for_display(
            self.get_display(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        servers = requests.get("https://servers.minetest.net/list").json()["list"]
        self.server_list.populate(servers)
        self.present()


if __name__ == "__main__":
    main()
