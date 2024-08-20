import os
import subprocess
import sys
import logging.config
from pathlib import Path

from exceptions import surplus_lines as exceptions
from logs.surplus_lines import LOGGING_CONFIG
from helper import validate_paths
from model.automation import Automator
from model.registrations import Producer

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)


class SurplusLinesAutomator:
    """TODO: Move self.app into the 'start' method, make it a local variable,  and pass
    it into the output dir method....
    NOTE: this actually may not be doable.. relook at it another time.
    """

    def __init__(self):
        self.app = Automator()
        self.user_doc_path: Path

    def output_dir(self, new_dir: str = None) -> str | None:
        if not new_dir and self.app.output_dir:
            return self.app.output_dir
        elif new_dir:
            _valid_dir = validate_paths(new_dir)
            self.app.output_dir = str(_valid_dir)
        else:
            return None

    def start(self, doc_path: str, producer_template: str) -> bool:
        if not self.app.output_dir:
            log.info(
                msg="The output folder isn't set. This needs to be set before proceeding with the program. ",
            )
            exceptions.spawn_message(
                "Warning",
                """Please choose a folder to save the final, stamped file
                in first. Click 'OK' here first, then click the 'Browse' button to select your desired folder.""",
                0x10 | 0x0,
            )
            raise exceptions.OutputDirNotSet()
        else:
            try:
                self.user_doc_path: Path = validate_paths(pathnames=doc_path)
            except OSError as e:
                msg = f"The file provided to the program is not a valid file.\nPath: {doc_path}"
                log.warning(msg=msg)
                exceptions.spawn_message(
                    "Warning",
                    msg,
                    0x10 | 0x0,
                )
                return False
            else:
                
                self.app.user_doc_path = self.user_doc_path
                self.app.exited = False
                log.info(
                    msg="Saved the PDF's path. Destroying the UI window.",
                )
                log.debug(
                    msg="The PDF path is: {0}".format(self.user_doc_path),
                )
                producer = Producer(
                    name=producer_template["name"],
                    pname=producer_template["pname"],
                    paddress=producer_template["paddress"],
                    city_st_zip=producer_template["city_st_zip"],
                )
            if self._automate(producer):
                return True
            else:
                return False

    def _automate(self, producer: Producer) -> bool:
        if not self.app.exited:
            
            self.app.payloads = None
            self.app.payloads = []
            self.app.parse_doc()
            stamp_num = 1
            stamp_paths = []
            for payload in self.app.payloads:
                log.debug(
                    msg="Current payload: {0}".format(payload),
                )
                log.info(
                    msg="Performing the web call.",
                )
                form_data = self.app.perform_web_call(payload, producer)
                log.info(
                    msg="Secured the response and formatted it.",
                )
                log.debug(
                    msg="The formatted response is: {0}.".format(form_data),
                )
                stamp_paths.append(self.app.fill_docs(form_data, stamp_num))
                stamp_num += 1
        # except exceptions.DocError:
        #     return False
        # except Exception as e:
        #     print(str(e))
        #     log.error(msg=str(e), stack_info=True)
        #     return False
        
            log.info(
                msg="Combining stamps into your document.",
            )
            new_file_path = self.app.combine_docs(stamp_paths)
            log.info(
                msg="Stamps combined. The stamped file location is: {0}.".format(
                    new_file_path
                ),
            )
            file_browser_path = os.path.join(os.getenv("WINDIR"), "explorer.exe")
            log.info(
                msg="Opening a file window to show you the new, stamped file.  The file will be highlighted for your convenience.",
            )
            log.debug(
                msg="File Explorer path used: {0}.".format(file_browser_path),
            )
            subprocess.run([file_browser_path, "/select,", new_file_path])
            log.debug(
                msg="Initializing and showing notification box via ToastNotifier.",
            )
