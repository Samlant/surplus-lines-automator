import ctypes

from win10toast import ToastNotifier

from exceptions.surplus_lines import OutputDirNotSet
from helper import TRAY_ICON, open_config
from interface import SurplusLinesAutomator
from model.registrations import (
    process_save,
    process_retrieval,
    standardize_name,
    validate_name,
    Producer,
)
from themes.palettes import BlueRose
from view.drag_n_drop import SurplusLinesView as View
from view.tray_icon import TrayIcon


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

    def process_SL_doc(self, event, producer_template: str):  # used by view
        doc_path = event.data.strip("{}")
        config = open_config()
        producer = config.get_section(name=producer_template).to_dict()
        try:
            interface.start(doc_path, producer)
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

    def save_output_dir(self, save_path: str):  # used by view
        interface.output_dir(new_dir=save_path)
        self.view.output_dir = save_path
        config = open_config()
        config.set("surplus lines", option="output_dir", value=save_path)

    def add_registration(self, event=None):
        template_names = self.view.reg_tv.get_all_names()
        name = standardize_name(self.view.template_name)
        if validate_name(template_names, name):
            producer = Producer(
                name=name,
                pname=self.view.producer_name,
                paddress=self.view.producer_address,
                city_st_zip=self.view.city_st_zip,
            )
            self.view.reg_tv.add_registration(producer)
            self.view.template_name = ""
            self.view.producer_name = ""
            self.view.producer_address = ""
            self.view.city_st_zip = ""
        else:
            ctypes.windll.user32.MessageBoxW(
                0,
                "A form already exists with this name. Please change the form name to a unique name and try adding again.",
                "Warning",
                0x10 | 0x0,
            )

    def btn_save_register_tab(self):
        row_data = self.view.reg_tv.get_all_rows()
        return process_save(
            row_data=row_data,
        )

    def btn_revert_register_tab(self):
        self.view.reg_tv.delete(*self.view.reg_tv.get_children())
        templates = process_retrieval()
        for template in templates:
            self.view.reg_tv.add_registration(template)
        return True

    def update_dropdown_options(self, start: bool = False):
        templates = []
        _ = process_retrieval()
        for template in _:
            templates.append(template.name)
        if start:
            return templates
        else:
            menu = self.view.producer_dropdown["menu"]
            menu.delete(0, "end")
            for template in templates:
                menu.add_command(
                    label=template,
                    command=lambda value=template: self.view._producer_template.set(
                        value
                    ),
                )


if __name__ == "__main__":
    presenter = Presenter(view=sl_view)
    tray_icon = TrayIcon(presenter=presenter)
    thread1 = tray_icon.create_icon(src_icon=str(TRAY_ICON))
    thread1.start()

    output_dir = interface.output_dir()
    with_initial_option = ["Choose a template"]
    templates = presenter.update_dropdown_options(start=True)
    for template in templates:
        with_initial_option.append(template)
    sl_view.make_view(
        presenter=presenter,
        output_dir=output_dir,
        template_values=with_initial_option,
    )
