from dataclasses import dataclass
from tkinter import ttk
from typing import Protocol


class Producer(Protocol):
    """Stores the characteristics of a specific PDF quoteform.

    Attributes:
        id : standardized name used to ID mapping in config.ini file
        name : user-chosen name for the specific mapping
        all other attrs : required fields from PDF

    """

    id: str
    name: str
    address: str


@dataclass
class RegColumn:
    name: str
    text: str
    width: int


class RegColumns:
    def __init__(self):
        self.objects = []
        self.names = []

    def add_column(self, name: str, text: str, width: int):
        x = RegColumn(name, text, width)
        self.objects.append(x)
        self.names.append(name)


class CurrentRegistrations(ttk.Treeview):
    def __init__(self, parent):
        columns = RegColumns()

        columns.add_column("name", "Template Name", 190)
        columns.add_column("pname", "Producer Name", 270)
        columns.add_column("paddress", "Street Address", 240)
        columns.add_column("city_st_zip", "City, State, Zip", 150)

        super().__init__(
            parent,
            columns=columns.names,
            show="headings",
            height=6,
        )
        for column in columns.objects:
            self.column(
                column.name,
                width=column.width,
                stretch=False,
            )

            self.heading(
                column.name,
                text=column.text,
                anchor="w",
            )

    def get_tv(self):
        return self

    def add_registration(self, producer: Producer):
        self.insert(
            "",
            "end",
            text=producer.name,
            values=producer.values(),
        )

    def remove_registration(self):
        current_item = self.selection()
        self.delete(current_item)

    def get_all_rows(self) -> list[list[str]]:
        row_data = []
        for parent in self.get_children():
            registration = self.item(parent)["values"]
            row_data.append(registration)
        return row_data

    # def get_quoteforms(self) -> list[Producer]:
    #     rows = self.get_all_rows()
    #     for row in rows:
    #         pass

    def get_all_names(self) -> list[str]:
        form_names = []
        items = self.get_children()
        if items:
            for item in items:
                registration = self.item(item)["values"][0]
                form_names.append(registration)
        return form_names
