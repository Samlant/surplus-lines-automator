from datetime import datetime
from pathlib import Path
import logging

import datefinder

from exceptions import surplus_lines as exceptions

from model.carriers.base import CarrierBuilder

log = logging.getLogger(__name__)


class YachtinsureBuilder(CarrierBuilder):
    def __init__(self, pdf_path: Path, pages: list[list[str]]) -> None:
        super().__init__(pdf_path, pages)
        self.name = "Yachtinsure"

    def get_user_doc_type(self) -> str:
        "This is correct 12/7"
        finder = {
            "quote": "QUOTATION",
            "policy": "Declarations page",
            "ap": "Additional Premium",
            "cancel": "CANCELLATION ENDORSEMENT",
            "renewal": "Renewal",
            "rp": "Return Premium",
        }
        x = self.pages[0]
        for doc_type, keyword in finder.items():
            try:
                x.index(keyword)
            except ValueError:
                continue
            else:
                log.debug(msg="", exc_info=1)
                self.user_doc_type = doc_type
                if doc_type != "rp" or doc_type != "cancel":
                    self.insert_page_index = len(self.pages)
                return doc_type
        raise exceptions.UnknownDocType(self)

    def get_client_name(self) -> bool:
        "this is correct 12/7"
        if self.user_doc_type == "cancel":
            for block in self.pages[0]:
                if "Insured Name/ Company:":
                    x = block.partition("Company:")[2]
        else:
            for block in self.pages[0]:
                if "Insured:" in block:
                    x = block.partition("Insured:")[2]
        self.client_name = x.strip()

    def get_eff_date(self) -> datetime:
        "This is correct 12/7"
        if self.user_doc_type == "cancel":
            txt = "Endorsement Effective:"
        else:
            txt = "Date:"
        for block in self.pages[0]:
            if txt in block:
                x = block.partition(txt)[2]
                dates = datefinder.find_dates(x)
                y = []
                for date in dates:
                    y.append(date)
                date_obj = y[0]
                if not isinstance(date_obj, datetime):
                    raise TypeError
                self.eff_date = date_obj.strftime("%m/%d/%Y")
                return date_obj

    def get_premiums(self) -> bool:
        "This is correct 12/7"
        if self.user_doc_type == "cancel":
            txt = "Total Return"
        else:
            txt = "Total Amount Due:"
        for page in self.pages:
            for block in page:
                if txt in block:
                    x = block.partition(txt)[2].strip()
                    x = x.partition("USD")[2].lstrip()
                    if self.user_doc_type == "cancel":
                        x = x.partition(" ")[0]
                    self.premiums.append(float(x.replace(",", "").strip()))

    def get_policy_nums(self) -> bool:
        "This is correct 12/7"
        if self.user_doc_type == "quote":
            txt = "Quote Number"
        else:
            txt = "Policy Number"
        for block in self.pages[0]:
            if txt in block:
                x = block.partition(":")[2].lstrip().partition(" ")[0]
                self.premiums.append(x.strip())
