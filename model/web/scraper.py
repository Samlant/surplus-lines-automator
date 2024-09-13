from dataclasses import dataclass
from typing import Protocol
import logging

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

log = logging.getLogger(__name__)

xpaths = {
    "tax": "//table[@class='tax-invoice tax-assessments'][1]/tbody[1]/tr[2]/td[2]",
    "service": "//table[@class='tax-invoice tax-assessments'][1]/tbody[1]/tr[4]/td[2]",
    "subtotal_fees": "//table[@class='tax-invoice tax-assessments'][1]/tbody[1]/tr[6]/td[2]",
    "total": "//table[@class='tax-invoice tax-assessments'][1]/tbody[1]/tr[7]/td[2]",
}

for k, v in xpaths.items():
    log.debug(
        msg="The {0} xpath is currently: {1}".format(k, v),
    )


class Payload(Protocol):
    coverage_code: int | str
    transaction_type: int | str
    tax_status: int | str
    premium: float | str
    policy_fee: float | str
    uri: str
    eff_date: str


@dataclass
class Response:
    tax: str = None
    service: str = None
    subtotal_fees: str = None
    total: str = None

    def get_dict(self) -> dict[str, str]:
        return {
            "tax": self.tax,
            "service_fee": self.service,
            "subtotal_fees": self.subtotal_fees,
            "total_cost": self.total,
        }


class Driver:
    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.page_load_strategy = "normal"
        self.driver: webdriver.Edge = None
        # self.service = Service(executable_path=browser_driver)


    def send_call(self, payload: Payload) -> None:
        log.info(
            msg="Assigning Edge webdriver to scraper",
        )
        log.debug(
            msg="Webdriver's options: {0}".format(self.options),
        )
        self.driver = webdriver.Edge(
            options=self.options,
        )
        self.driver.get(
            payload.uri,
        )
        log.info(
            msg="Launching web UI",
        )
        log.debug(
            msg="Website URI: {0}".format(payload.uri),
        )
        # Key inputs
        self.driver.find_element(value="PolicyEffectiveDate").send_keys(
            payload.eff_date,
        )
        log.debug(
            msg="Found policy Eff Date field, inserted: {0}".format(payload.eff_date),
        )
        self.driver.find_element(value="TransactionEffectiveDate").send_keys(
            payload.eff_date,
        )
        log.debug(
            msg="Found trans Eff Date field, inserted: {0}".format(payload.eff_date),
        )
        # SelectLists
        coverage = self.driver.find_element(value="CoverageCode")
        coverage_select = Select(coverage)
        coverage_select.select_by_value(
            value=payload.coverage_code,
        )
        log.debug(
            msg="Found coverage code field, inserted: {0}".format(
                payload.coverage_code
            ),
        )

        transaction = self.driver.find_element(value="TransactionType")
        transaction_select = Select(transaction)
        transaction_select.select_by_value(
            value=payload.transaction_type,
        )
        log.debug(
            msg="Found trans type field, inserted: {0}".format(
                payload.transaction_type
            ),
        )

        tax_status = self.driver.find_element(value="TaxStatus")
        tax_status_select = Select(tax_status)
        tax_status_select.select_by_value(
            payload.tax_status,
        )
        log.debug(
            msg="Found Tax Status field, inserted: {0}".format(payload.tax_status),
        )
        # Key inputs
        self.driver.find_element(value="Premium").send_keys(
            payload.premium,
        )
        log.debug(
            msg="Found premium field, inserted: {0}".format(payload.premium),
        )
        self.driver.find_element(value="PolicyFee").send_keys(
            payload.policy_fee,
        )
        log.debug(
            msg="Found policy fee field, inserted: {0}".format(payload.policy_fee),
        )
        log.info(
            msg="Inserted data into fields, scrolling to submit btn.",
        )
        # btn
        element = self.wait_for_element(self.driver, By.ID, "btnSubmit",)
        self.scroll_and_click(self.driver, element)
    

        ##############################
        # Refactored below code into separate functions
        ##############################
        # WebDriverWait(self.driver, 10).until(
        #     expected_conditions.element_to_be_clickable((By.ID, "btnSubmit"))
        # )
        # element = self.driver.find_element(value="btnSubmit")
        # # self.driver.execute_script(
        # #     "arguments[0].scrollIntoView(true);",
        # #     element,
        # # )
        # actions = ActionChains(self.driver)
        # self.scroll_shim(self.driver, element)
        # actions.move_to_element(element)
        # actions.perform()
        # try:
        #     element.click()
        # except ElementClickInterceptedException:
        #     log.info(
        #         msg="Scrolling failed/incomplete, trying to scroll and click once more.",
        #     )
        #     try:
        #         self.driver.execute_script(
        #             "arguments[0].scrollIntoView(true);",
        #             element,
        #         )
        #         element.click()
        #     except ElementClickInterceptedException:
        #         try:
        #             # Scroll to the top of the page
        #             self.driver.execute_script("window.scrollTo(0, 0);")
        #             # Scroll down to the button
        #             self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        #             element.click()
        #         except ElementClickInterceptedException:

        log.debug(msg="Scrolled into view of submit btn and clicked it.")

    def wait_for_element(self, driver, by, value, timeout=10):
        return WebDriverWait(driver, timeout).until(
            expected_conditions.element_to_be_clickable((by, value))
        )

    def scroll_and_click(self, driver, element):
        if not self.try_scroll_shim(driver, element):
            if not self.try_scroll_js(driver, element):
                if not self.try_scroll_js(driver, element, position="top"):
                    if not self.try_scroll_js(driver, element, position="bottom"):
                        log.error("All attempts to scroll and click the button failed.")

    def try_scroll_shim(self, driver, element, actions=None):
        try:
            if actions is None:
                actions = ActionChains(driver)
            self.scroll_shim(driver, element)
            actions.move_to_element(element)
            actions.perform()
            element.click()
            return True
        except ElementClickInterceptedException:
            log.info("Scrolling failed/incomplete, trying next method.")
            return False
        
    def try_scroll_js(self, driver, element, position=None):
        try:
            if position == "top":
                driver.execute_script("window.scrollTo(0, 0);")
            elif position == "bottom":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            return True
        except ElementClickInterceptedException:
            log.info("JavaScript scrolling failed, trying next method.")
            return False

    def scroll_shim(self, passed_in_driver, _object):
        x = _object.location["x"]
        y = _object.location["y"]
        scroll_by_coord = f"window.scrollTo({x},{y});"
        scroll_nav_out_of_way = "window.scrollBy(0, -120);"
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way)

    # Tax
    def get_response(self) -> Response:
        r = Response()
        for key, path in xpaths.items():
            value = self.driver.find_element(
                by=By.XPATH,
                value=path,
            ).text
            log.debug(
                msg="Found {0}, and its value is: {1}".format(key, value),
            )
            setattr(r, key, value)
        log.debug(
            msg="Returning Response: {0}".format(str(r)),
        )
        return r
