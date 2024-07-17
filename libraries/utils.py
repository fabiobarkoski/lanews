from datetime import datetime

from RPA.Browser.Selenium import Selenium
from SeleniumLibrary import WebElement
from dateutil.relativedelta import relativedelta

def get_element_attribute(driver: Selenium, locator: str, attr: str, parent: WebElement) -> str:
    element = driver.find_element(locator, parent)
    attribute = driver.get_element_attribute(element, attr)
    return attribute

def element_exist(driver: Selenium, locator: str, parent: WebElement) -> True:
    try:
        driver.find_element(locator, parent)
        return True
    except Exception:
        return False

def parse_months(months: int) -> datetime:
    base_date = datetime.now()
    base_date = datetime(base_date.year, base_date.month, 1)
    if months > 1:
        return base_date - relativedelta(months=(months-1))
    return base_date