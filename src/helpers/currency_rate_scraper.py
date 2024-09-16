from bs4 import BeautifulSoup
import requests
import csv
import tempfile
import os
import urllib.parse
from zipfile import ZipFile
from io import BytesIO
from datetime import datetime
from src.logger.logger import logger


class CurrencyRateScraper:
    def __init__(self) -> None:
        self.__base_url = os.environ["EURO_BANK_CURRENCY_URL"]
        # self.__base_url = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"

    def __get_soup(self):
        page = requests.get(self.__base_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def find_zip_file_link(self):
        soup = self.__get_soup()
        h2_element = soup.find('h2', string="Downloads")
        download_links_element = h2_element.find_next_sibling(
            class_="-link-icons")
        zip_file_element = download_links_element.findChild(
            'a', class_="download")
        if zip_file_element.has_attr('href'):
            url_suffix = zip_file_element.attrs['href']
            parsed_url = urllib.parse.urlparse(self.__base_url)
            parsed_url = parsed_url._replace(path=url_suffix)
            return parsed_url.geturl()

    def dowload_and_read_csv(self, file_link):
        page = requests.get(file_link)
        zip_file = ZipFile(BytesIO(page.content))
        tmpdirname = tempfile.TemporaryDirectory()
        csv_file_name = zip_file.namelist()[0]
        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.info('tmpdirname: {}'.format(tmpdirname))
            zip_file.extractall(path=tmpdirname)
            arr = os.listdir(tmpdirname)
            logger.info('arr: {}'.format(arr))
            csv_path = os.path.join(tmpdirname, csv_file_name)
            with open(csv_path, mode='r') as file:
                csv_file = csv.reader(file)
                lines = []
                for row in csv_file:
                    lines.append(row)
                return lines

    def postprocess(self, csv_data):
        date = csv_data[1][0]
        n = len(csv_data[0])
        currency_map = {}
        for i in range(1, n):
            currency_name = csv_data[0][i].strip()
            currency_value = csv_data[1][i].strip()
            if currency_name and currency_value:
                currency_map[currency_name] = currency_value
        logger.info('date: {}'.format(date))
        logger.info('currency_map: {}'.format(currency_map))
        date_dt = datetime.strptime(
            date, '%d %B %Y')
        return date_dt, currency_map

    def execute(self):
        file_link = self.find_zip_file_link()
        csv_data = self.dowload_and_read_csv(file_link)
        return self.postprocess(csv_data)

    def parse_date_from_site(self):
        soup = self.__get_soup()
        txt_element = soup.find(
            'p', string="All currencies quoted against the euro (base currency)")
        date_element = txt_element.find_previous()
        date_dt = datetime.strptime(date_element.text, '%d %B %Y')
        logger.info('date_dt: {}'.format(date_dt))
        return date_dt
