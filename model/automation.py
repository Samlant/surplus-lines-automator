from dataclasses import dataclass
from pathlib import Path
import logging

from helper import open_config, validate_paths
from exceptions import surplus_lines as exceptions
from model.carriers.base import Carrier
from model.doc.filler import DocFiller
from model.doc.parser import DocParser
from model.web.scraper import Driver, Response


log = logging.getLogger(__name__)


@dataclass
class Payload:
    """Holds data to be inputted into the FSL website"""

    policy_num: str | int
    premium: float
    eff_date: str
    transaction_type: int | str

    def __post_init__(self):
        # static vars below:
        self.coverage_code: int | str = "3006"
        self.tax_status: int | str = "0"
        self.policy_fee: int = 0
        self.uri: str = "https://www.fslso.com/tax-estimator"


class Automator:
    def __init__(self):
        self._user_doc_path: Path = None
        self.payloads: list[Payload] = []
        self.form_data: dict[str, float | str] = None
        self.exited: bool = False
        self.carrier_obj: Carrier = None
        self.stamps: list[Path] = []
        self.doc_filler: DocFiller = None
        self.root = None

    @property
    def output_dir(self) -> str:
        config = open_config()
        _dir = config.get(
            "surplus lines",
            "output_dir",
        ).value
        try:
            output_dir = validate_paths(pathnames=_dir)
        except OSError as e:
            return None
        else:
            return str(output_dir)

    @output_dir.setter
    def output_dir(self, new_dir: str) -> bool:
        config = open_config()
        config.set(section="surplus lines", option="output_dir", value=new_dir)
        config.update_file()
        if config.get(section="surplus lines", option="output_dir").value == new_dir:
            return True
        else:
            return False

    @property
    def user_doc_path(self):
        return self._user_doc_path

    @user_doc_path.setter
    def user_doc_path(self, doc_path: str):
        log.info(msg="Saving the PDF's path.")
        log.debug(
            msg=f"Event data: {doc_path}",
        )
        self._user_doc_path = doc_path

        # def install_placeholders(self):
        # #####################################################################
        # #####################################################################
        # #####################################################################
        # ################ IMPLEMENT THIS HERE! ########################
        #     if self.output_dir:
        #         log.debug(
        #             msg="output_dir detected, prefilling Text box with its path: {0}".format(
        #                 self.output_dir
        #             ),
        #         )
        #         self.output_path.insert("1.0", self.output_dir)
        #     else:
        #         log.info(
        #             msg="No output folder selected.  Please choose a folder to save the finalized, stamped file in before dragging a PDF file onto the window.",
        #         )
        #     log.debug(
        #         msg="Spawning window, starting mainloop.",
        #     )
        #     self.root.mainloop()

    #####################################################################
    #####################################################################
    #####################################################################
    #####################################################################

    def parse_doc(self):
        """Saves premium & eff date into a Payload object."""
        log.debug(
            msg="Initializing DocParser class with user doc path: {0}.".format(
                self.user_doc_path
            ),
        )
        try:
            dp = None
            dp = DocParser(pdf_path=self.user_doc_path)
        except exceptions.UnknownDocType as e:
            exceptions.spawn_message("Error", str(e), 0x10 | 0x0)
            # btn = OK
            # exit SL window and terminate thread
            log.warning(
                msg="{0}".format(str(e)),
                exc_info=1,
            )
            raise exceptions.DocError(self.user_doc_path) from e
        try:
            carrier_builder, trans_type = dp.build_market_class(self.user_doc_path)
        except exceptions.DocParseError as e:
            log.warning(
                msg=str(e),
            )
            output = exceptions.spawn_message("Error", str(e), 5)
            if output == 4:
                # btn = retry
                self.restart_GUI()
                log.info(
                    msg="User decided to restart and try again.",
                    exc_info=1,
                )
            else:
                # btn = cancel
                # exit SL window and terminate thread
                log.info(
                    msg="User decided to cancel instead of trying again. Exiting.",
                    exc_info=1,
                )
                raise exceptions.DocParseError(dp.market) from e
        except exceptions.UnsupportedDocType as e:
            output = exceptions.spawn_message("Error", str(e), 5)
            if output == 4:
                # btn = retry
                log.info(
                    msg="User decided to restart and try again.",
                    exc_info=1,
                )
                self.restart_GUI()
            else:
                # btn = cancel
                # exit SL window and terminate thread
                log.info(
                    msg="User decided to cancel instead of trying again. Exiting.",
                    exc_info=1,
                )
                raise exceptions.UnsupportedDocType(dp.market) from e
        except exceptions.UnknownDocType as e:
            exceptions.spawn_message("Error", str(e), 0x10 | 0x0)
            # btn = OK
            # exit SL window and terminate thread
            log.warning(
                msg="{0}".format(str(e)),
                exc_info=1,
            )
            raise exceptions.UnknownDocType(dp.market) from e
        # we moved below exception onto a lower level to handle with a retry
        # attempt if user confirms okay to override error.
        # except exceptions.SurplusLinesNotApplicable as e:
        #     exceptions.spawn_message("Error", str(e), 0x10 | 0x0)
        #     # btn = OK
        #     # exit SL window and terminate thread
        #     log.warning(
        #         msg="{0}".format(str(e)),
        #         exc_info=1,
        #     )
        #     raise exceptions.SurplusLinesNotApplicable(dp.market) from e
        else:
            log.debug(
                msg="Starting to build carrier object using the CarrierBuilder.",
            )
            self.carrier_obj = carrier_builder.build(self.user_doc_path)
            for premium, policy_num in zip(
                self.carrier_obj.premiums, self.carrier_obj.policy_nums
            ):
                log.debug(
                    msg="Zipping together the premiums and policy nums, then iterating over them to add to the payload object.",
                )
                log.debug(
                    msg="Current Premium: {0}. Current Policy Num: {1}".format(
                        premium, policy_num
                    ),
                )
                payload = Payload(
                    policy_num=policy_num,
                    premium=premium,
                    eff_date=self.carrier_obj.eff_date,
                    transaction_type=trans_type,
                )
                self.payloads.append(payload)
            log.debug(
                msg="The finalized payload object is: {0}".format(self.payloads),
            )

    def perform_web_call(self, payload: Payload, producer) -> dict[str, float | str]:
        log.info(
            msg="Initializing the web driver.",
        )
        driver = Driver()
        log.info(
            msg="Sending the web call loaded with the payload from the PDF file.",
        )
        driver.send_call(payload)
        log.info(
            msg="Getting the response.",
        )
        response = self._get_response(driver)
        return self._format_response(response, payload, producer)

    def _get_response(self, driver: Driver) -> Response:
        response: Response = driver.get_response()
        return response

    def _format_response(
        self,
        response: Response,
        payload: Payload,
        producer,
    ) -> dict[str, float | str]:
        form_data = {
            "tax": "",
            "service_fee": "",
            "subtotal_fees": "",
            "total_cost": "",
        }
        for key, value in response.get_dict().items():
            x = value.replace("$", "").replace(",", "")
            if "(" in x:
                y = float(x.replace("(", "").replace(")", ""))
                x = -abs(y)
            form_data[key] = "{:,.2f}".format(float(x))
        return self.__data_to_dict(form_data, payload, producer)

    def __data_to_dict(
        self,
        form_data: dict,
        payload: Payload,
        producer,
    ) -> dict[str, float | str]:
        other_data = {
            "insured_name": self.carrier_obj.client_name,
            "policy_num": payload.policy_num,
            "premium": "{:,.2f}".format(payload.premium),
            "policy_fee": "{:,.2f}".format(payload.policy_fee),
            "eff_from": self.carrier_obj.eff_date,
            "eff_to": self.carrier_obj.exp_date,
            "producing_agent_name": producer.pname,
            "producing_agent_address1": producer.paddress,
            "producing_agent_address2": producer.city_st_zip,
        }
        form_data.update(other_data)
        return form_data

    def fill_docs(self, form_data: dict[str, float | str], stamp_num: int) -> Path:
        log.debug(
            msg="Initializing DocFiller class. Processing doc with stamp number: {0}".format(
                stamp_num
            ),
        )
        doc_filler = DocFiller(self.output_dir)
        stamp_path = doc_filler.process_doc(form_data, stamp_num)
        return stamp_path

    def combine_docs(self, stamps: list[Path]):
        doc_filler = DocFiller(self.output_dir)
        log.debug(
            msg="Using these stamps: {0}, and inserting into page index: {1}, inside user doc path: {2}".format(
                stamps, self.user_doc_path, self.carrier_obj.insert_page_index
            ),
        )
        new_path = doc_filler.combine_stamps_into_pdf(
            self.user_doc_path,
            stamps,
            self.carrier_obj.insert_page_index,
        )
        for stamp in stamps:
            stamp.unlink()
        return new_path

    def restart_GUI(self):
        self.market = None
        self.spawn_window()
