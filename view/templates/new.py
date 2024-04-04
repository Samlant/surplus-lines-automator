from tkinter import ttk
from typing import Protocol


class Presenter(Protocol):
    def add_registration(self) -> None: ...


class NewRegistrations(ttk.LabelFrame):
    def __init__(
        self,
        presenter: Presenter,
        parent,
        view,
        text: str,
    ):
        super().__init__(master=parent, text=text)

        ttk.Label(
            self,
            text="Enter a name for the template, then the name & address of the producer.",
        ).grid(column=0, row=0, pady=3, columnspan=5)
        ttk.Label(
            master=self,
            text="Template Name:",
        ).grid(column=0, row=1, padx=(3, 0))
        template_name_entry = ttk.Entry(
            master=self,
            name="template_name",
            textvariable=view._template_name,
            width=80,
        )
        template_name_entry.grid(
            column=1,
            row=1,
            sticky="ew",
            ipady=5,
            pady=1,
            padx=3,
        )

        ttk.Label(
            master=self,
            text="Producer Name:",
        ).grid(column=0, row=2, padx=(3, 0))
        pname_entry = ttk.Entry(
            master=self,
            name="fname",
            textvariable=view._producer_name,
            width=80,
        )
        pname_entry.grid(
            column=1,
            row=2,
            sticky="ew",
            ipady=5,
            pady=1,
            padx=3,
        )

        ttk.Label(
            self,
            text="Producer Address:",
        ).grid(column=0, row=3, padx=(3, 0))
        paddress = ttk.Entry(
            master=self,
            name="p_addy",
            textvariable=view._producer_address,
            width=80,
        )
        paddress.grid(
            column=1,
            row=3,
            sticky="ew",
            ipady=5,
            pady=5,
            padx=3,
        )
        ttk.Label(
            self,
            text="City, State & Zip:",
        ).grid(column=0, row=3, padx=(3, 0))
        paddress = ttk.Entry(
            master=self,
            name="city_st_zip",
            textvariable=view._city_st_zip,
            width=80,
        )
        paddress.grid(
            column=1,
            row=3,
            sticky="ew",
            ipady=5,
            pady=5,
            padx=3,
        )

        ttk.Button(
            master=self,
            text="Register",
            command=presenter.add_registration,
        ).grid(
            rowspan=3,
            column=2,
            row=1,
            sticky="ew",
            padx=5,
            pady=10,
            ipady=30,
        )
