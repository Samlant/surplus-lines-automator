from datetime import datetime
from pathlib import Path
import logging

import datefinder

from exceptions import surplus_lines as exceptions
from model.carriers.base import CarrierBuilder

log = logging.getLogger(__name__)


### CONCEPT IS FINISHED! CONGRATS!
class ConceptBuilder(CarrierBuilder):
    def __init__(self, pdf_path: Path, pages: list[list[str]]) -> None:
        super().__init__(pdf_path, pages)
        self.name = "Concept"

    def get_user_doc_type(self) -> str:
        "This is complete 12/7"
        # Note that Concept uses the single right quotation mark,  not the quote on US keyboards...
        finder = {
            "quote": "Quotation",
            "binder": "Temporary Binder",
            "policy": "Cover Note",
            "renewal": "Renewal Quotation",
            "endt": "Policy Endorsement",
        }
        endt_finder = {
            "ap": "Additional Premium",
            "cancel": "hereunder is cancelled",
            "rp": "Return Premium",
        }
        x = self.pages[0]
        for doc_type, keyword in finder.items():
            log.debug(
                msg="Running checks to detect if user_doc is of type '{0}'.".format(
                    doc_type
                ),
            )
            try:
                x.index(keyword)
            except ValueError:
                continue
            else:
                log.debug(
                    msg="Found matching block via index() method using keyword: '{0}'.".format(
                        keyword
                    ),
                )
                if doc_type == "endt":
                    for block in x:
                        for doc_type, keyword in endt_finder.items():
                            log.debug(
                                msg="Running checks to detect if user_doc is of type '{0}'.".format(
                                    doc_type
                                ),
                            )
                            if keyword in block:
                                log.debug(
                                    msg="Found match! The keyword was: {0}, and the detected block was: {1}".format(
                                        keyword, block
                                    ),
                                )
                                self.user_doc_type = doc_type
                                self.insert_page_index = self.find_insert_index()
                                return doc_type
                else:
                    self.user_doc_type = doc_type
                    self.insert_page_index = self.find_insert_index()
                    # self.insert_page_index = 2 # This is an old, static method...
                    return doc_type
        log.debug(
            msg="Did not match any keywords.  Initial finder dict: {0},  second endorsement finder dict: {1}, and the page's contents are: {2}".format(
                finder, endt_finder, x
            ),
            exc_info=1,
        )
        raise exceptions.UnknownDocType(self)

    def find_insert_index(self) -> int:
        if self.user_doc_type == "ap" or self.user_doc_type == "rp" or self.user_doc_type == "cancel":
            return len(self.pages)
        else:
            for i, block in enumerate(self.pages[2]):
                if "1. Definitions" in block:
                    return 2
            return 3

    def get_client_name(self) -> bool:
        "This is complete 12/7"
        if self.user_doc_type == "quote" or self.user_doc_type == "renewal":
            txt = "Applicant:"
        else:
            txt = "Assured:"
        i = self.pages[0].index(txt)
        i += 1
        self.client_name = self.pages[0][i].strip()
        return True

    def get_eff_date(self) -> datetime:
        "This is complete 12/7"
        if self.user_doc_type == "quote":
            i = self.pages[0].index("Date:")
            i += 1
        elif self.user_doc_type == "binder" or self.user_doc_type == "policy":
            i = self.pages[0].index("Period of Cover:")
            i += 1
        else:
            for i, block in enumerate(self.pages[0]):
                if "with effect from" in block:
                    break
        x = self.pages[0][i]
        x = x.replace("00.01", "")
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
        carrier_fee = 50
        if self.multiple_stamps_flag:
            for i, block in enumerate(self.pages[1]):
                if "Insurance Provider" in block:
                    i += 1
                    if (
                        "Accelerant Specialty" in self.pages[1][i]
                        and "Texas Insurance" in self.pages[1][i]
                        and "Hadron" in self.pages[1][i]
                        and "Palomar" in self.pages[1][i]
                        and "Lloyd's Syndicates" in self.pages[1][i]
                    ):
                        if "except" in self.pages[1][i]:
                            x: tuple[str,str,str] = self.pages[1][i].partition("except")
                            premium1_str = x[0].rpartition("US$")[2].strip().replace(",", "")
                            premium1 = float(premium1_str)
                            premium1 += carrier_fee
                            premium2 = (
                                x[2]
                                .rpartition("premium US$")[2]
                                .strip()
                                .replace(",", "")
                            )

                            for premium in [premium1, premium2]:
                                self.premiums.append(
                                    float(premium),
                                )
                        else:
                            pass
                    else:
                        raise exceptions.DocParseError(self)
        else:
            if (
                (self.user_doc_type == "policy")
                or (self.user_doc_type == "renewal")
                or (self.user_doc_type == "binder")
                or (self.user_doc_type == "quote")
            ):
                i = self.pages[0].index("Total Premium:")
                i += 1
                x = self.pages[0][i].partition("US$")[2].partition("cancelling")[0]
                premium = x.strip().replace(",", "")
                premium = float(premium)
                premium += carrier_fee
            elif (
                self.user_doc_type == "cancel"
                or self.user_doc_type == "rp"
                or self.user_doc_type == "ap"
            ):
                for block in self.pages[0]:
                    if "US$" in block:
                        x = block.partition("US$")[2]
                        premium = x.lstrip().partition(" ")[0].strip().replace(",", "")
                        premium = float(premium)
            else:
                raise ValueError
            self.premiums.append(premium)
        return True

    def get_policy_nums(self) -> bool:
        "This is correct 12/7"
        if self.user_doc_type == "quote" or self.user_doc_type == "renewal":
            txt = "Quote Number:"
        else:
            txt = "Declaration Number:"
        i = self.pages[0].index(txt)
        i += 1
        if self.multiple_stamps_flag:
            policy1 = self.pages[0][i].strip()
            self.policy_nums.append(policy1)
            for i, block in enumerate(self.pages[1]):
                if "Insurance Provider" in block:
                    i += 1
                    x = self.pages[1][i].partition("per UMR")[2]
                    policy2 = x.partition(")")[0].partition("(")[0].strip()
                    self.policy_nums.append(policy2)
        else:
            self.policy_nums.append(self.pages[0][i].strip())
        return True

    # --------------------------------------------------------
    # We commented out this function because we no longer
    # need to publish two separate stamps for excess liability
    # policies.  This class will instead inherit the function
    # from its parent class.
    # If this changes in teh future, uncomment this function.
    # --------------------------------------------------------
    # def check_for_multiple_stamps(self) -> bool:
    #     """Checks if multiple stamps are needed and sets the
    #     multiple_Stamps_flag to True is so.

    #     This is corect 12/7"""
    #     for page in self.pages:
    #         for i, block in enumerate(page):
    #             if "Insurance Providers:" in block:
    #                 log.debug(
    #                     msg="Detected 'Insurance Providers' in text block, now checking for the 'except' keyword. block contents: {0}".format(
    #                         block
    #                     ),
    #                 )
    #                 i += 1
    #                 if "except" in page[i] or "US$" in page[i].partition("US$")[2]:
    #                     log.debug(
    #                         msg="Found 'except' keyword in block, block's contents are: {0}".format(
    #                             block
    #                         ),
    #                     )
    #                     self.multiple_stamps_flag = True
    #                     return True
    #     return True
