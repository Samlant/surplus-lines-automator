from tkinter.ttk import Style


def create_style(master_object, palette) -> Style:
    s = Style(master_object)
    p = palette
    s.theme_use("alt")
    s = _assign_default_static_colors(s, p)
    s = _map_default_dynamic_colors(s, p)
    s = _assign_custom_static_colors(s, p)
    s = _map_custom_dynamic_colors(s, p)
    return s


def _assign_default_static_colors(style_object, palette):
    s = style_object
    s.configure(
        "TNotebook",
        background=palette.base_bg_color,
    )

    s.configure(
        "TFrame",
        background=palette.base_bg_color,
    )
    s.configure(
        "TLabelframe",
        background=palette.base_bg_color,
    )
    s.configure(
        "TLabelframe.Label",
        background=palette.base_bg_color,
        font=("helvetica", 14, "normal"),
    )
    s.configure(
        "TButton",
        background=palette.btn_base_bg,
        foreground=palette.btn_fg,
        font=("helvetica", 12, "bold"),
    )
    # s.configure(
    #     "TCheckbutton",
    #     indicatorbackground="black",
    #     indicatorforeground="white",
    #     background="black",
    #     foreground="white",
    # )
    # s.configure(
    #     "TCheckbutton",
    #     background=palette.alt_bg_color,
    #     foreground=palette.alt_fg_color,
    #     indicatorcolor="black",
    #     selectbackground=palette.chck_btn_select_color,
    #     font=("helvetica", 12, "normal"),
    #     relief="raised",
    # )
    s.configure(
        "TEntry",
        background=palette.alt_bg_color,
        fieldbackground=palette.alt_bg_color,
        selectbackground=palette.alt_fg_color,
        selectforeground=palette.alt_bg_color,
        foreground=palette.alt_fg_color,
    )
    s.configure(
        "TLabel",
        background=palette.base_bg_color,
        foreground=palette.base_fg_color,
    )
    # s.configure(
    #     "TMenubutton",
    #     background=palette.menuoption_bg_color,
    #     foreground=palette.menuoption_fg_color,
    #     highlightbackground=palette.menuoption_bg_color,
    #     activebackground="red",
    #     font=("helvetica", 12, "normal"),
    # )
    s.configure(
        "Treeview",
        background=palette.alt_bg_color,
        foreground=palette.alt_fg_color,
        fieldbackground=palette.alt_bg_color,
    )
    s.configure(
        "Treeview.field",
        fieldbackground=palette.alt_bg_color,
    )
    return s


def _map_default_dynamic_colors(style_obj, palette):
    s = style_obj
    s.map(
        "TNotebook",
        background=[("selected", palette.base_bg_color)],
    )
    s.map(
        "TButton",
        background=[
            ("pressed", palette.btn_pressed_bg),
            ("active", palette.btn_active_bg),
        ],
        foreground=[
            ("pressed", palette.btn_fg),
            ("active", palette.btn_fg),
        ],
    )
    return s


def _assign_custom_static_colors(style_obj, palette):
    s = style_obj
    s.configure(
        "Header.TLabel",
        font=("helvetica", 20, "normal"),
    )
    return s


def _map_custom_dynamic_colors(style_obj, palette):
    s = style_obj
    return s
