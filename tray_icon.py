import threading
from typing import Protocol

from PIL import Image
from pystray import Icon, Menu, MenuItem


class Presenter(Protocol):
    """This enables us to call funtions from the Presenter
    class, either to send/retrieve data.
    """

    def stop_program(self) -> None: ...

    def show_window(self) -> None: ...

    def window_is_open(self) -> None: ...


class TrayIcon:
    def __init__(self, presenter):
        self.presenter = presenter

    def _on_clicked(self, icon, item):
        if str(item) == "Add Surplus Lines Stamp":
            print("Running Surplus Lines Calculator")
            if self.presenter.window_is_open():
                print("Window is already open. Please exit that one prior to opening a new one.")
            else:
                self.presenter.show_window()
        elif str(item) == "Exit":
            icon.visible = False
            icon.stop()
            self.presenter.stop_program()

    def create_icon(self, src_icon):
        thread = threading.Thread(
            daemon=True,
            target=lambda: Icon(
                "test",
                Image.open(src_icon),
                menu=Menu(
                    MenuItem("Add Surplus Lines Stamp", self._on_clicked),
                    MenuItem("Exit", self._on_clicked),
                ),
            ).run(),
            name="Sys Tray Icon",
        )
        return thread
