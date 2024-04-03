from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)


@dataclass
class Carrier:
    """Finalized class for a carrier obj.  Used to provide formatted, validated data to the rest of the program.

    Notes: Do we really need all these attrs? Double-check!!

    Attributes:
        name -- name of carrier
        pdf_path -- used for error-handling/exceptions
        doc_type -- used for error-handling/exceptions
        client_name -- name of client
        eff_date -- eff date of policy
        exp_date -- exp date of policy
        policy_nums -- list of policy nums
        premiums -- list of premiums
        insert_page_index -- dictates where the stamps get inserted into

    """

    name: str
    pdf_path: Path
    doc_type: str
    client_name: str
    eff_date: str
    exp_date: str
    policy_nums: list[str]
    premiums: list[float]
    insert_page_index: int


class CarrierBuilder:
    def __init__(self, pdf_path: Path, pages: list[list[str]]):
        self.name: str = None
        self.pdf_path: Path = pdf_path
        self.pages: list[list[str]] = pages
        self.user_doc_type: str = None
        self.client_name: str = None
        self.eff_date: str = None
        self.exp_date: str = None
        self.policy_nums: list[str] = []
        self.premiums: list[int] = []
        self.multiple_stamps_flag: bool = False
        self.insert_page_index: int = 1

    def __str__(self) -> str:
        return f"{self.name}: doc_type={self.user_doc_type}, client={self.client_name}, effective={self.eff_date}, policy number(s)={self.policy_nums}, premium(s)={self.premiums}"

    def __repr__(self) -> str:
        return f"{self.name}('{self.pdf_path}')"

    # Builder Function
    def build(self, pdf_path: Path):
        return Carrier(
            name=self.name,
            pdf_path=pdf_path,
            doc_type=self.user_doc_type,
            client_name=self.client_name,
            eff_date=self.eff_date,
            exp_date=self.exp_date,
            policy_nums=self.policy_nums,
            premiums=self.premiums,
            insert_page_index=self.insert_page_index,
        )

    # Primary Required Functions
    def get_user_doc_type(self) -> str:
        pass

    def get_client_name(self) -> bool:
        pass

    def get_eff_date(self) -> datetime:
        pass

    def get_premiums(self) -> bool:
        pass

    def get_policy_nums(self) -> bool:
        pass

    # Secondary Helper Functions
    def check_if_doc_needs_stamp(self) -> bool:
        log.info(
            msg="{0} always requires stamps.".format(self.name),
        )
        return True

    def check_for_multiple_stamps(self) -> bool:
        log.info(
            msg="{0} doesn't require multiple stamps.".format(self.name),
        )
        return False

    def locate_correct_page(self, pdf_path) -> bool:
        pass
