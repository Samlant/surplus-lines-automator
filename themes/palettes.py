from dataclasses import dataclass, field


@dataclass
class Palette:
    base_bg_color: str
    base_fg_color: str
    alt_bg_color: str
    alt_fg_color: str
    dragdrop_bg_color: str
    menuoption_bg_color: str
    menuoption_fg_color: str
    btn_base_bg: str
    btn_active_bg: str
    btn_pressed_bg: str
    btn_fg: str
    chck_btn_bg: str
    chck_btn_fg: str
    chck_btn_select_color: str


@dataclass
class BlueRose(Palette):
    base_bg_color: str = field(default="#CFEBDF", init=False)
    base_fg_color: str = field(default="#5F634F", init=False)  # black or grey
    alt_bg_color: str = field(
        default="#5F634F", init=False
    )  # dark grey; for text inputs + chkbtns
    alt_fg_color: str = field(default="#FFCAB1", init=False)  # pink
    dragdrop_bg_color: str = field(
        default="#5F634F", init=False
    )  # temp: same as text inputs
    menuoption_bg_color: str = field(
        default="#5F634F", init=False
    )  # dark grey; same as text inputs
    menuoption_fg_color: str = field(default="#FFCAB1", init=False)  # pink
    btn_base_bg: str = field(default="#1D3461", init=False)
    btn_active_bg: str = field(default="#203b6f", init=False)
    btn_pressed_bg: str = field(default="#16294d", init=False)
    btn_fg: str = field(default="#CFEBDF", init=False)
    chck_btn_bg: str = field(default="#5F634F", init=False)
    chck_btn_fg: str = field(default="#FFCAB1", init=False)
    chck_btn_select_color: str = field(default="#000000", init=False)
