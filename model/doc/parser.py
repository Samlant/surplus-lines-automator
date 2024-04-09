from pathlib import Path
from datetime import date
import logging

import fitz

from exceptions import surplus_lines as exceptions
from model.carriers.base import CarrierBuilder
from model.carriers.builders.concept import ConceptBuilder
from model.carriers.builders.kemah import KemahBuilder
from model.carriers.builders.yachtinsure import (
    YachtinsureBuilder,
)


log = logging.getLogger(__name__)


class DocParser:
    def __init__(self, pdf_path):
        pages = self.get_first_three_pages(pdf_path)
        log.debug(
            msg="Saved first three pages of the user's doc",
        )
        self.market = self.identify_mrkt(pages, pdf_path)
        log.debug(
            msg="Identified the market as: {0}, and assigned the pages to the CarrierBuilder class.".format(self.market.name),
        )
        doc_type = self.market.get_user_doc_type()
        log.debug(
            msg="Identified the doc_type as: {0}".format(doc_type),
        )

        if isinstance(self.market, KemahBuilder) and doc_type == "policy":
            for block in pages[0]:
                if (
                    "Recreational Yacht Insurance Policy" in block
                    and "Declarations Page" not in block
                ):
                    log.debug(
                        msg="Dec Page not detected on first page... Locating Dec Page within the rest of the Kemah doc...",
                    )
                    doc = fitz.open(pdf_path)
                    start_indx = 15
                    log.debug(
                        msg="Opened user's doc, starting our search for the Dec Page at page index {0}".format(
                            start_indx
                        ),
                    )
                    end_indx = len(doc) - 1
                    if self.locate_policy_page(doc, start_indx, end_indx):
                        log.debug(
                            msg="Identified the Dec Page, it's contents are: {0}".format(
                                self.market.pages
                            ),
                        )
                    else:
                        start_indx = 1
                        log.debug(
                            msg="Did not identify Dec Page. Starting second search at page index {0}".format(
                                start_indx
                            ),
                            exc_info=1,
                        )
                        if self.locate_policy_page(doc, start_indx, 14):
                            log.debug(
                                msg="Identified the Dec Page, it's contents are: {0}".format(
                                    self.market.pages
                                ),
                                exc_info=1,
                            )
                        else:
                            log.debug(
                                msg="Failed to locate Dec Page. Raising DocParseError.",
                                exc_info=1,
                            )
                            raise exceptions.DocParseError(self.market)
        else:
            log.debug(
                msg="Assigned the page(s) to the market.",
                exc_info=1,
            )

    def identify_mrkt(self, pages: list[list[str]], pdf_path: Path) -> CarrierBuilder:
        for block in pages[0]:
            if "Concept Special Risks" in block:
                return ConceptBuilder(pdf_path, pages)
            elif "Sutton Specialty Insurance Company" in block:
                return KemahBuilder(pdf_path, pages[0])
            elif "yachtinsure" in block.lower():
                return YachtinsureBuilder(pdf_path, pages)
        log.debug(
            msg="Couldn't identify the market from user's doc. The PDF path was {0}. The pages were: {1}".format(
                pdf_path, pages
            ),
            exc_info=1,
        )
        raise exceptions.DocParseError(pdf_path)

    def build_market_class(self, pdf_path: Path) -> tuple[CarrierBuilder, str]:
        log.info(
            msg="Checking to ensure a stamp is required for this document.",
        )
        if not self.market.check_if_doc_needs_stamp():
            log.debug(
                msg="User's doc does not need stamping. Path to file: {0}".format(
                    pdf_path
                ),
                exc_info=1,
            )
            raise exceptions.SurplusLinesNotApplicable(self.market)
        log.info(
            msg="Getting client name.",
        )
        self.market.get_client_name()
        log.info(
            msg="Getting effective date.",
        )
        try:
            date_obj = self.market.get_eff_date()
        except TypeError:
            log.debug(
                msg="Returned date is not a Datetime obj after trying to get Eff date.",
                exc_info=1,
            )
            raise TypeError
        self.market.exp_date = self._add_one_year(date_obj).strftime("%m/%d/%Y")
        log.info(
            msg="Added one year to create the expiry date: {0}".format(
                self.market.exp_date
            ),
            exc_info=1,
        )
        trans_type = self._assign_transaction_type(self.market.user_doc_type)
        log.debug(
            msg="Assigned transaction type: {0}".format(trans_type),
        )
        self.market.check_for_multiple_stamps()
        log.info(
            msg="Finished checking for multiple stamps: {0}".format(
                self.market.pages
            ),
        )
        self.market.get_policy_nums()
        log.debug(
            msg="Identified policy numbers: {0}".format(self.market.policy_nums),
        )
        self.market.get_premiums()
        log.debug(
            msg="Identified premiums: {0}".format(self.market.premiums),
        )
        if self.market.user_doc_type == "cancel" or self.market.user_doc_type == "rp":
            premiums = []
            for premium in self.market.premiums:
                premiums.append(-abs(premium))
            self.market.premiums = premiums
        log.info(
            msg="Returning CarrierBuilder object and transaction type.",
        )
        log.debug(
            msg="CarrierBuilder object: {0}".format(self.market),
        )
        return self.market, trans_type

    def get_first_three_pages(self, pdf_path) -> list[list[str]]:
        doc = fitz.open(pdf_path)
        pages = []
        pages.append(self.get_page_contents(doc[0]))
        if len(doc) >= 2:
            pages.append(self.get_page_contents(doc[1]))
            if len(doc) >= 3:
                pages.append(self.get_page_contents(doc[2]))
        log.debug(
            msg="Finished saving up to the first 3 pages of user's doc. Total number of pages saved: {0}".format(
                len(pages)
            ),
            exc_info=1,
        )
        return pages

    def locate_policy_page(self, doc, start_indx: int, end_indx: int) -> bool:
        _index = start_indx
        while _index <= end_indx:
            page = self.get_page_contents(doc[_index])
            try:
                page.index("5. Declarations Page")
            except ValueError:
                _index += 1
            else:
                self.market.insert_page_index = _index + 1
                # self.market.pages.append(doc[_index])
                self.market.pages = page
                log.debug(
                    msg="Identified the dec page and assigned the insert_page_index as {0}.  Added Dec Page to the market's pages attr.".format(
                        self.market.insert_page_index
                    ),
                    exc_info=1,
                )
                return True
        return False

    @staticmethod
    def get_page_contents(pg) -> list[str]:
        blocks = pg.get_text("blocks", sort=True)
        page = []
        for block in blocks:
            interim = block[4].replace("’", "'")
            formatted = interim.strip().replace("\n", " ")
            page.append(formatted)
        # log.debug(
        #     msg="Finished saving the formatted blocks within the page. Formatted page results: {0}".format(
        #         page
        #     ),
        #     exc_info=1,
        # )
        return page

    @staticmethod
    def _add_one_year(date_obj):
        "Adds 1 year to a datetime obj (such as eff date) and accounts for leap years"
        try:
            return date_obj.replace(year=date_obj.year + 1)
        except ValueError:
            log.info(
                msg="Identified a leap year when adding one year to datetime object. Adding one year using the alternative method.",
            )
            return date_obj + (
                date(date_obj.year + 1, 1, 1) - date(date_obj.year, 1, 1)
            )

    @staticmethod
    def _assign_transaction_type(doc_type) -> str:
        if (doc_type == "quote") or (doc_type == "binder") or (doc_type == "policy"):
            return "1"
        elif doc_type == "renewal":
            return "5"
        elif doc_type == "ap":
            return "2"
        elif doc_type == "rp":
            return "3"
        elif doc_type == "cancel":
            return "4"
        else:
            log.debug(
                msg="No transaction type values matched doc_type: {0}".format(doc_type),
                exc_info=1,
            )
            raise ValueError("Recheck transaction type assignment!")
