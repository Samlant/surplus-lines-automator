import logging
from tkinter import ttk, Text, filedialog, StringVar, Toplevel
from typing import Protocol
import threading

from tkinterdnd2 import DND_FILES, TkinterDnD

from themes.applicator import create_style
from .templates.new import NewRegistrations
from .templates.registrations import make_registration_widgets


class Presenter(Protocol):
    def process_SL_doc(self, event): ...

    def save_output_dir(self, save_path: str): ...

    def update_dropdown_options(self, start: bool = False): ...


log = logging.getLogger(__name__)


class SurplusLinesView:
    def __init__(self, view_palette):
        self.root: TkinterDnD = TkinterDnD.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.palette = view_palette
        self.style = None
        self.presenter: Presenter = None
        self.producer_templates_list: list[str] = []
        self._producer_template = StringVar(
            master=self.root,
            name="producer_template",
        )
        self._template_name = StringVar(
            master=self.root,
            name="template_name",
        )
        self._producer_name = StringVar(
            master=self.root,
            name="producer_name",
        )
        self._producer_address = StringVar(
            master=self.root,
            name="producer_address",
        )
        self._city_st_zip = StringVar(
            master=self.root,
            name="city_st_zip",
        )

    @property
    def templates(self) -> dict[str, str]:
        return {
            "template_name": self.template_name,
            "pname": self.producer_name,
            "paddress": self.producer_address,
            "city_st_zip": self.city_st_zip,
        }

    @templates.setter
    def templates(self, save_data: dict[str, str | bool]) -> None:
        for attr_name, value in save_data.items():
            setattr(self, attr_name, value)

    @templates.deleter
    def templates(self):
        self.template_name = ""
        self.producer_name = ""
        self.producer_address = ""

    @property
    def producer_template(self) -> str:
        return self._producer_template.get()

    @producer_template.setter
    def producer_template(self, new_template: str):
        self._producer_template.set(new_template)

    @property
    def template_name(self) -> str:
        return self._template_name.get()

    @template_name.setter
    def template_name(self, new_template: str):
        self._template_name.set(new_template)

    @property
    def producer_name(self) -> str:
        return self._producer_name.get()

    @producer_name.setter
    def producer_name(self, new_name: str):
        self._producer_name.set(new_name)

    @property
    def producer_address(self) -> str:
        return self._producer_address.get()

    @producer_address.setter
    def producer_address(self, new_address: str):
        self._producer_address.set(new_address)

    @property
    def city_st_zip(self) -> str:
        return self._city_st_zip.get()

    @city_st_zip.setter
    def city_st_zip(self, new_address: str):
        self._city_st_zip.set(new_address)

    @property
    def output_dir(self) -> str:
        self._output_dir.get("1.0", "end-1c")

    @output_dir.setter
    def output_dir(self, new_output_dir) -> None:
        del self.output_dir
        self._output_dir.insert("1.0", new_output_dir)

    @output_dir.deleter
    def output_dir(self) -> None:
        self._output_dir.delete("1.0", "end")

    @property
    def doc_path(self) -> str:
        self._doc_path.get("1.0", "end-1c")

    @doc_path.setter
    def doc_path(self, new_doc_path) -> None:
        del self._doc_path
        self._doc_path.insert("1.0", new_doc_path)

    @doc_path.deleter
    def doc_path(self) -> None:
        self._doc_path.delete("1.0", "end")

    def make_view(
        self,
        presenter,
        output_dir: str | None,
        template_values: list[str],
    ):
        self.presenter = presenter
        self.style = create_style(self.root, self.palette)
        self._assign_window_traits()
        self.producer_templates_list = template_values
        self.producer_template = "Choose a template"
        self._create_widgets()
        if output_dir:
            self.output_dir = output_dir
        self.root.withdraw()
        self.root.mainloop()

    def on_close(self, window=None):
        if window:
            self.root.attributes("-topmost", True)
            window.destroy()
            self.presenter.update_dropdown_options()
        else:
            print("hiding window")
            self.root.withdraw()

    def _assign_window_traits(self):
        self.root.geometry("730x290")
        self.root.configure(background="#5F9EA0")
        self.root.attributes("-topmost", True)
        self.root.title("FSL AutoFiller")
        self.root.attributes("-alpha", 0.95)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        log.debug(
            msg="Window attributes are set., creating frames for UI.",
        )

    def _create_widgets(self):
        log.debug(
            msg="Creating widgets for SL UI.",
        )
        top = ttk.Frame(self.root)
        top.pack(
            fill="x",
            expand=False,
            side="top",
            padx=3,
            pady=(5, 0),
        )
        middle1 = ttk.Frame(self.root)
        middle1.pack(
            fill="both",
            expand=False,
            side="top",
            padx=3,
        )
        middle2 = ttk.Frame(self.root)
        middle2.pack(
            fill="both",
            expand=True,
            side="top",
            padx=3,
            pady=(4, 0),
        )
        middle3 = ttk.Frame(self.root)
        middle3.pack(
            fill="both",
            expand=True,
            side="top",
            padx=3,
            pady=(4, 0),
        )
        bottom = ttk.Frame(self.root)
        bottom.pack(
            fill="both",
            expand=True,
            side="top",
            padx=3,
            pady=3,
        )
        log.debug(
            msg="Created frames for UI, setting labels",
        )
        ttk.Label(
            top,
            text="FIRST TIME USERS!",
            font=("Times New Roman", 14, "bold"),
        ).pack(side="left", anchor="se")
        ttk.Label(
            middle1,
            text="↪",
            font=("Times New Roman", 30, "bold"),
        ).pack(side="left")
        ttk.Label(
            middle1,
            text="Choose save location for the stamped doc:",
        ).pack(side="left")
        #### INSERT MenuOption ####
        ttk.Label(
            middle2,
            text="Producer Template to use:",
            font=("Times New Roman", 12, "bold"),
        ).pack(
            side="left",
            pady=1,
            padx=2,
        )
        self.producer_dropdown = ttk.OptionMenu(
            middle2,
            self._producer_template,
            *self.producer_templates_list,
        )
        self.producer_dropdown.pack(
            fill="x",
            side="left",
            pady=1,
            padx=2,
            ipadx=100,
        )
        ttk.Button(
            master=middle2,
            command=self.spawn_options_window,
            text="Edit Templates",
        ).pack(fill="x", side="right")
        #### END SECTION ####
        ttk.Label(
            middle3,
            text="Drag-N-Drop your document below!",
            font=("Times New Roman", 18, "bold"),
        ).pack(
            side="top",
        )
        log.debug(
            msg="Created labels for UI, creating button.",
        )
        ttk.Button(
            middle1,
            command=self._browse_output_dir,
            text="Browse",
        ).pack(
            side="left",
            padx=3,
            pady=3,
        )
        log.debug(
            msg="Created button for UI, creating drag-n-drop Text box.",
        )
        self._output_dir = Text(
            master=middle1,
            foreground=self.palette.alt_fg_color,
            background=self.palette.alt_bg_color,
            highlightcolor=self.palette.alt_bg_color,
            selectbackground=self.palette.alt_fg_color,
            selectforeground=self.palette.alt_bg_color,
            height=2,
            width=48,
        )
        self._output_dir.pack(
            side="left",
            padx=3,
            ipady=0,
        )

        self._doc_path = Text(
            bottom,
            foreground=self.palette.alt_fg_color,
            background=self.palette.alt_bg_color,
            highlightcolor=self.palette.alt_bg_color,
            selectbackground=self.palette.alt_fg_color,
            selectforeground=self.palette.alt_bg_color,
            name="user_doc_path",
        )
        self._doc_path.drop_target_register(DND_FILES)
        self._doc_path.dnd_bind(
            "<<Drop>>",
            self.process_file,
        )
        self._doc_path.pack(
            fill="both",
            expand=True,
            ipady=5,
        )
        log.debug(
            msg="Created and activated drag-n-drop for Text box.",
        )

    def _browse_output_dir(self):
        try:
            _dir = filedialog.askdirectory(mustexist=True)
        except AttributeError as e:
            log.info(
                msg="The Folder Browser window must have been closed before user clicked 'OK'. Continuing on.",
            )
            log.debug(
                msg=f"Caught {e}, continuing on.",
            )
        else:
            if _dir == "":
                pass
            else:
                self.presenter.save_output_dir(save_path=_dir)

    def process_file(self, event):
        t = threading.Thread(
            target=lambda: self.presenter.process_SL_doc(
                event=event, producer_template=self.producer_template
            ),
            daemon=True,
        )
        t.start()
        self.root.withdraw()

    def spawn_options_window(self, event=None):
        new_window = Toplevel(master=self.root)
        self.root.attributes("-topmost", False)
        new_window.attributes("-topmost", True)
        new_window.attributes("-alpha", 0.95)
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.on_close(new_window))
        frame = ttk.Frame(master=new_window, style="TFrame")
        frame.pack(fill="both")
        make_registration_widgets(
            view=self,
            presenter=self.presenter,
            parent=frame,
        )
        self.presenter.btn_revert_register_tab()
