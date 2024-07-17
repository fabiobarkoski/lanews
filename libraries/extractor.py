import os
import time
import logging
import zipfile
from glob import glob
from pathlib import Path
from datetime import datetime

import requests
from RPA.Excel.Files import Files
from SeleniumLibrary import WebElement
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems

from libraries.news import News, Picture
from libraries.utils import element_exist, get_element_attribute, parse_months

OUTPUT_DIR = Path(os.getenv("ROBOT_ARTIFACTS", "output"))
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=logging.INFO)

class Extractor:
    news: list[News] = []
    url = "https://www.latimes.com/"

    def __init__(self) -> None:
        self.driver = Selenium()
        work_items = WorkItems()
        work_items.get_input_work_item()
        self.variables = work_items.get_work_item_variables()

    def run(self):
        self.driver.open_chrome_browser(self.url)
        self.driver.click_element("data:element:search-button")
        self.driver.press_keys("data:element:search-form-input", self.variables["phrase"])
        self.driver.press_key("data:element:search-form-input", r"\13")
        self.check_topic(self.variables.get("topics"))
        self.search_news()
        self.generate_file()
        self.zip_pictures()

    def check_topic(self, topics_list: list[str]):
        logger.info(f"topics: {topics_list}")
        for topic in topics_list:
            self.driver.click_element("data:toggle-trigger:see-all")
            topics_element = self.driver.find_element("data:name:Topics")
            topics_element = self.driver.find_elements("tag:label", parent=topics_element)
            for index, t in enumerate(topics_element):
                if t.text.lower() == topic.lower():
                    self.driver.execute_javascript(f'document.getElementsByClassName("checkbox-input-label")[{index}].click()')
                    self.driver.wait_until_element_is_visible("class:search-results-module-filters-selected", 10)
                    time.sleep(1)
                    self.driver.wait_until_element_is_visible("tag:ps-promo", 10)
                    break

    def search_news(self):
        base_date = parse_months(self.variables["period"])
        stop_search = True
        while stop_search:
            elements = self.driver.find_elements("tag:ps-promo")
            for e in elements:
                timestamp = get_element_attribute(self.driver, "class:promo-timestamp", "data-timestamp", e)
                date = datetime.fromtimestamp(int(timestamp)/1000)
                if date < base_date:
                    stop_search = False
                    break
                self.get_news(e)
            if stop_search:
                self.driver.click_element("class:search-results-module-next-page")

    def get_news(self, element: WebElement):
        title = self.driver.find_element("class:promo-title", element).text
        if element_exist(self.driver, "class:promo-description", element):
            description = self.driver.find_element("class:promo-description", element).text
        else:
            description = None
        timestamp = get_element_attribute(self.driver, "class:promo-timestamp", "data-timestamp", element)
        date = datetime.fromtimestamp(int(timestamp)/1000)
        if element_exist(self.driver, "css:picture img", element):
            img = get_element_attribute(self.driver, "css:picture img", "src", element)
            filename = img.split("%")[-1][2:]
            picture_name = f"{filename}.jpeg" if "." not in filename else filename
        else:
            picture_name = None
        self.news.append(
            News(
                title=title,
                date=date,
                description=description,
                picture=Picture(picture_name, img) if picture_name else None,
                count=News.count_phrases([title, description], self.variables["phrase"]),
                contains_money=News.contains_money([title, description])
            )
        )

    def download_picture(self, picture: Picture):
        if not os.path.exists(f"{OUTPUT_DIR}/pictures"):
            logger.info("creating pictures dir")
            os.mkdir(f"{OUTPUT_DIR}/pictures")
        res = requests.get(picture.link)
        if res.status_code == 200:
            with open(f"{OUTPUT_DIR}/pictures/"+picture.name, "wb") as f:
                f.write(res.content)

    def generate_file(self):
        excel = Files()
        excel.create_workbook()
        for n in self.news:
            if n.picture:
                self.download_picture(n.picture)
            excel.append_rows_to_worksheet(n.to_dict(), header=True)
        excel.save_workbook(f"{OUTPUT_DIR}/output.xlsx")
    
    def zip_pictures(self):
        files = glob(f"{OUTPUT_DIR}/pictures/*")
        if files:
            logger.info("zipping pictures")
            with zipfile.ZipFile(f"{OUTPUT_DIR}/pictures.zip", "w", zipfile.ZIP_DEFLATED) as zf:
                for file in files:
                    zf.write(os.path.relpath(file), os.path.basename(file))
                    