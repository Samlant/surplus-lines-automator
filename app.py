from themes.palettes import BlueRose
from view import SurplusLinesView as View
from tray_icon import TrayIcon
from interface import SurplusLinesAutomator
from exceptions.surplus_lines import OutputDirNotSet
from helper import TRAY_ICON, open_config
from win10toast import ToastNotifier

palette = BlueRose()
sl_view = View(view_palette=palette)
interface = SurplusLinesAutomator()

class Presenter:
    def __init__(self, view: View) -> None:
        self.view = view

    def show_window(self):
        self.view.root.deiconify()

    def window_is_open(self) -> bool:
        if self.view.root.winfo_viewable():
            return True
        else:
            return False
    def stop_program(self):
        self.view.root.destroy()
    
    def process_SL_doc(self, event): # used by view
        doc_path = event.data.strip("{}")
        try:
            interface.start(doc_path)
        except OutputDirNotSet:
            self.show_window()
        else:
            toaster = ToastNotifier()
            toaster.show_toast(
                "SUCCESS! Your doc is now stamped.",
                "A new window will show you the finished file.",
                duration=5,
            )
            # self.view.root.withdraw()

    def save_output_dir(self, save_path: str): # used by view
        interface.output_dir(new_dir=save_path)
        self.view.output_dir = save_path
        config = open_config()
        config.set("surplus lines", option="output_dir", value=save_path)


if __name__ == "__main__":
    presenter = Presenter(view=sl_view)
    tray_icon = TrayIcon(presenter=presenter)
    thread1 = tray_icon.create_icon(src_icon=str(TRAY_ICON))
    thread1.start()
    output_dir = interface.output_dir()
    
    sl_view.make_view(
        presenter=presenter,
        output_dir=output_dir,
    )