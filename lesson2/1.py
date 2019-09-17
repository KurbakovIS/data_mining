import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import lxml
import random
import time


class Utils:
    def __init__(self, url):
        self.url = url

    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0'

    def get_response(self):
        return requests.get(self.url, headers={'User-Agent': self.USER_AGENT})

    def get_soup(self):
        return BeautifulSoup(self.get_response().text, 'lxml')

    def get_body(self):
        return self.get_soup().html.body


class ParseHH(Utils):
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0'
    base_url = 'https://hh.ru'
    client = MongoClient('localhost', 27017)
    database = client.HH
    collection = database.jsJob

    def __init__(self, url):
        self.url = url
        super().__init__(url)

    def get_urlPagination(self):
        listPagination = Utils.get_body(self).findAll('a', attrs={'class': 'bloko-button HH-Pager-Control'})
        paginationsUrl = [f'{self.base_url}{itm.attrs["href"]}' for itm in listPagination]
        return paginationsUrl

    def get_catalogItem(self):
        catalogItem = []
        for url in self.get_urlPagination():
            response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
            soup = BeautifulSoup(response.text, 'lxml')
            soupBody = soup.html.body
            catalogItem.append(soupBody.findAll('div', attrs={'class': 'vacancy-serp-item'}))
            time.sleep(random.randint(1, 4))
        return catalogItem

    def get_itemUrls(self):
        listUrls = []
        for items in self.get_catalogItem():
            listUrls.append([f'{itm.find("a").attrs["href"]}' for itm in items])
        return listUrls

    def req_item(self):
        priceMin = ''
        priceMax = ''
        result_list = []

        for urls in self.get_itemUrls():
            for url in urls:
                response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
                soup = BeautifulSoup(response.text, 'lxml')
                soupBody = soup.html.body

                title = soupBody.find('h1', attrs={'itemprop': 'title'}).text
                price = soupBody.find('p', attrs={'class': 'vacancy-salary'}).text
                urlJobStill = soupBody.find('a', attrs={'class': 'vacancy-company-name'})['href']

                if 'до' in price:
                    try:
                        priceMin = price.split('до')[0].split(' ')[1].replace(u'\xa0', '')
                    except IndexError:
                        print(price)
                        priceMin = None
                    try:
                        priceMax = price.split('до')[1].split(' ')[1].replace(u'\xa0', '')
                    except TypeError:
                        priceMax = None
                elif ' з/п не указана'.replace(' ', '') in price.replace(' ', ''):
                    priceMin = None
                    priceMax = None
                elif 'от' in price and (not 'до' in price):
                    priceMin = price.split(' ')[1].replace(u'\xa0', '')
                    priceMax = None

                result = {
                    'title': title,
                    'priceMin': priceMin,
                    'priceMax': priceMax,
                    'urlJobStill': f'{self.base_url}{urlJobStill}',
                    'url': response.url,
                }
                result_list.append(result)
                print(result_list)
                time.sleep(random.randint(1, 4))
        return result_list

    def insert_database(self):
        for itm in self.req_item():
            print(itm)
            self.collection.insert_one(itm)


if __name__ == "__main__":
    job = input('Введите наименование вакансии: ')
    catalog = ParseHH(f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={job}')
    # t = catalog.req_item()
    catalog.insert_database()
print(1)
