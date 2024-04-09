from pathlib import Path
import logging

from datetime import datetime
from exceptions import surplus_lines as exceptions

from model.carriers.base import CarrierBuilder

log = logging.getLogger(__name__)

class KemahBuilder(CarrierBuilder):
    def __init__(self, pdf_path: Path, pages: list[str]) -> None:
        super().__init__(pdf_path, pages)
        self.name = "Kemah"
        self.applicable_states = [
            "FL",
        ]

    def get_user_doc_type(self) -> str:
        "This is complete 12/7"
        finder = {
            "quote": "Recreational Yacht Insurance Quote",
            "binder": "Recreational Yacht Insurance Binder",
            "policy change": "Policy Changes",
            "policy": [
                "Declarations Page",
                "Recreational Yacht Insurance Policy",
            ],
        }
        for doc_type, keyword in finder.items():
            log.debug(
                msg="Running checks to detect if user_doc is of type '{0}'.".format(
                    doc_type
                ),
            )
            if doc_type == "policy":
                for block in self.pages:
                    if keyword[0] in block or keyword[1] in block:
                        log.debug(
                            msg="Detected to be a '{0}'. The detected block was: {1}".format(
                                doc_type, block
                            ),
                        )
                        self.user_doc_type = doc_type
                        return doc_type
            try:
                self.pages.index(keyword)
            except ValueError:
                continue
            else:
                log.debug(
                    msg="Found matching block via index() method using keyword: '{0}'.".format(
                        keyword
                    ),
                )
                if doc_type == "policy change":
                    rates = self._get_change_rates()
                    if 0 not in rates["ap"]:
                        self.user_doc_type = "ap"
                    elif "Policy Cancellation" in self.pages[0]:
                        self.user_doc_type = "cancel"
                    elif 0 not in rates["rp"]:
                        self.user_doc_type = "rp"
                    else:
                        raise exceptions.UnknownDocType(self)
                else:
                    self.user_doc_type = doc_type
                return True
        raise exceptions.UnknownDocType(self)

    def get_client_name(self) -> bool:
        "This is complete 12/7"
        if self.user_doc_type == "quote":
            txt = "Applicant:"
        else:
            txt = "Insured:"
        for block in self.pages:
            if txt in block:
                if "Additional" not in block:
                    log.debug(
                        msg="Detected matching block: '{0}'.".format(block),
                    )
                    self.client_name = block.partition(txt)[2].strip()
                    log.info(
                        msg="Client's name: '{0}'.".format(self.client_name),
                    )
                    return True

    def get_eff_date(self) -> datetime:
        "This is complete 12/7"
        if self.user_doc_type == "policy" or self.user_doc_type == "binder":
            txt = "Date of Issue:"
            for block in self.pages:
                if txt in block:
                    _ = block.partition(txt)[2].strip()
                    log.debug(
                        msg="Detected matching block using '{0}'. target: '{1}', within block: '{2}'".format(
                            txt, _, block
                        ),
                    )
        elif self.user_doc_type == "quote":
            txt = "60 days from"
            for block in self.pages:
                
                if txt in block:
                    _ = block.partition(txt)[2].strip()
                    log.debug(
                        msg="Detected matching block using '{0}'. target: '{1}', within block: '{2}'".format(
                            txt, _, block
                        ),
                    )
        elif (
            self.user_doc_type == "cancel"
            or self.user_doc_type == "rp"
            or self.user_doc_type == "ap"
        ):
            txt = "Effective Date:"
            for block in self.pages:
                if txt in block:
                    _ = block.partition(txt)[2]
                    log.debug(
                        msg="Detected matching block using '{0}'. target: '{1}', within block: '{2}'".format(
                            txt, _, block
                        ),
                    )
            unformatted_date = _.partition("at")[0].strip()
            log.debug(
                msg="Unformatted_date: {0}".format(unformatted_date),
            )
            date_obj = datetime.strptime(unformatted_date, "%d %b %Y")
            if not isinstance(date_obj, datetime):
                raise TypeError
            self.eff_date = date_obj.strftime("%m/%d/%Y")
            log.info(
                msg="Got and formatted the effective date: {0}".format(self.eff_date),
            )
            return date_obj
        else:
            raise ValueError(
                """
                Parsing for the doc_type failed.  Recheck 
                parsing procedure for user_doc_type.
                """
            )
        date_obj = datetime.strptime(_, "%B %d, %Y")
        if not isinstance(date_obj, datetime):
            raise TypeError
        self.eff_date = date_obj.strftime("%m/%d/%Y")
        log.info(
            msg="Got and formatted the effective date: {0}".format(self.eff_date),
        )
        return date_obj

    def get_premiums(self) -> bool:
        "This is complete 12/7"
        if (
            self.user_doc_type == "cancel"
            or self.user_doc_type == "rp"
            or self.user_doc_type == "ap"
        ):
            rates = self._get_change_rates()
            if (
                "XX" not in rates["ap"]
                and rates["ap"] != 0
                and "XX" not in rates["taxes"]
                and rates["taxes"] != 0
            ):
                log.debug(
                    msg="Detected premium as AP with taxes. AP: {0}, taxes: {1}.".format(
                        rates["ap"], rates["taxes"]
                    ),
                )
                x = rates["ap"] + rates["taxes"]
                self.premiums.append(x)
            elif "XX" not in rates["ap"] and rates["ap"] != 0 and rates["taxes"] == 0:
                log.debug(
                    msg="Detected premium as AP without taxes. AP: {0}".format(
                        rates["ap"]
                    ),
                )
                self.premiums.append(rates["ap"])
            elif (
                "XX" not in rates["rp"]
                and rates["rp"] != 0
                and "XX" not in rates["taxes"]
                and rates["taxes"] != 0
            ):
                log.debug(
                    msg="Detected premium as RP with taxes. RP: {0}, taxes: {1}.".format(
                        rates["rp"], rates["taxes"]
                    ),
                )
                x = rates["rp"] + rates["taxes"]
                self.premiums.append(x)
            else:
                log.debug(
                    msg="Detected premium as RP without taxes. RP: {0}".format(
                        rates["rp"]
                    ),
                )
                self.premiums.append(rates["rp"])
        else:
            for block in self.pages:
                
                txt = "Total"
                if txt in block:
                    log.debug(
                        msg="Matched block using text: '{0}'. The matched block is: {1}".format(
                            txt, block
                        ),
                    )
                    x = block.partition("Total")[2].partition("$")[2]
                    log.debug(
                        msg="Before stripping whitespace and commas, the premium is: '{0}'".format(
                            x
                        ),
                    )
                    self.premiums.append(float(x.replace(",", "").strip()))
        return True

    def get_policy_nums(self) -> bool:
        "This is complete 12/7"
        if self.user_doc_type == "quote":
            self.policy_nums.append("TBA")
        else:
            txt = "Policy Number:"
            for block in self.pages:
                if txt in block:
                    _ = block.partition(txt)[2].lstrip()
                    log.debug(
                        msg="Matched block using text: '{0}'. The matched block is: '{1}'. The target is: '{2}".format(
                            txt, block, _
                        ),
                    )
                    self.policy_nums.append(_.partition(" ")[0])

    def check_if_doc_needs_stamp(self) -> bool:
        "This is complete 12/7"
        if (
            self.user_doc_type == "binder"
            or self.user_doc_type == "policy"
            or self.user_doc_type == "quote"
        ):
            if self.user_doc_type == "quote":
                txt = "Applicant"
            else:
                txt = "Insured"
            for i, block in enumerate(self.pages):
                if txt in block and not "Additional" in block:
                    log.debug(
                        msg="Matched block using text: '{0}'. The matched block is: '{1}'.".format(
                            txt, block
                        ),
                    )
                    log.debug(
                        msg="Moving to the next subsequent block.",
                    )
                    i += 1
                    # for _i, u in enumerate(self.pages):
                    for state in self.applicable_states:
                        log.info(
                            msg="Comparing client's address against applicable Surplus Lines state(s)...",
                        )
                        if self.pages[i] == "":
                            # Sometimes, this item is not captured from the PDF, so this catches
                            # those instances and assumes user is correct in stmaping it
                            return True
                        elif state in self.pages[i]:
                            log.debug(
                                msg="Matched block using text: '{0}'. The matched block is: '{1}'.".format(
                                    state, block
                                ),
                            )
                            return True
                    return False
        elif (
            self.user_doc_type == "cancel"
            or self.user_doc_type == "ap"
            or self.user_doc_type == "rp"
        ):
            
            for block in self.pages:
                txt = "Surcharge"
                if txt in block:
                    if "XX" in block:
                        log.debug(
                            msg="Matched block using text: '{0}'. The matched block is: '{1}'.".format(
                                txt, block
                            ),
                        )
                        return True
                    else:
                        return False

    def _get_change_rates(self) -> dict[str, float]:
        "This is complete 12/7"
        for i, block in enumerate(self.pages):
            txt = "Additional Premium"
            if txt in block:
                log.debug(
                    msg="Matched text with block! Text: '{0}', block: '{1}'.".format(
                        txt, block
                    ),
                )
                rates = {
                    "ap": i,
                    "rp": i + 1,
                    "taxes": i + 2,
                }
                log.debug(
                    msg="Indexes for all rates: {0}".format(rates),
                )
        for key, value in rates.items():
            value = self.__parse_change_rate(self.pages[value])
            rates[key] = value
        return rates

    def __parse_change_rate(self, string) -> float:
        "This is complete 12/7"
        log.debug(
            msg="Parsing '{0}' for rates!".format(string),
        )
        num = string.partition("$")[2]
        log.debug(
            msg="Checking '{0}' for XX's or integers...".format(num),
        )
        if "XX" in num:
            log.debug(
                msg="Detected XX's.",
            )
            return 0
        else:
            num = float(num.replace(",", "").strip())
            log.debug(
                msg="Did not detect XX's. Float value: {0}".format(num),
            )
        if "-" in string:
            log.debug(
                msg="Detected to be a negative number because a minus sign (-) is present in string: '{1}'. Returning {2}".format(
                    "-", string, -num
                ),
            )
            return -num
        else:
            return num
