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


class ParseAvito(Utils):
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0'
    base_url = 'https://www.avito.ru/'
    client = MongoClient('localhost', 27017)
    database = client.Avito
    collection = database.apartment

    def __init__(self, url):
        self.url = url
        super().__init__(url)

    # def get_response(self):
    #     return super(ParseAvito, self).get_response()
    #
    # def get_soup(self):
    #     return super(ParseAvito, self).get_soup()
    #
    # def get_body(self):
    #     return super(ParseAvito, self).get_body()

    def get_urlPagination(self):
        listPagination = Utils.get_body(self).find('div', attrs={'class': 'pagination-pages'})
        paginationsUrl = [f'{self.base_url}{itm.attrs["href"]}' for itm in listPagination.findAll('a')]
        paginationsUrl.reverse()
        paginationsUrl.append(Utils.get_response(self).url)
        paginationsUrl.reverse()
        return paginationsUrl

    def get_catalogItem(self):
        catalogItem = []
        for url in self.get_urlPagination():
            response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
            soup = BeautifulSoup(response.text, 'lxml')
            soupBody = soup.html.body
            catalogItem.append(soupBody.findAll('div', attrs={'class': 'js-catalog-item-enum'}))
            time.sleep(random.randint(1, 4))
        return catalogItem

    def get_itemUrls(self):
        listUrls=[]
        for items in self.get_catalogItem():
            listUrls.append([f'{self.base_url}{itm.find("a").attrs["href"]}' for itm in items])
        return listUrls

    def req_item(self):
        result_list = []
        for urls in self.get_itemUrls():
            for url in urls:
                response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
                soup = BeautifulSoup(response.text, 'lxml')
                soupBody = soup.html.body
                try:
                    price = soupBody.find('span', attrs={'itemprop': 'price'})['content']
                except IndexError:
                    price = None
                except TypeError:
                    price = None
                seller = soupBody.find('div', attrs={'class': 'seller-info-name'}).text.split(' ')[1].rstrip()
                try:
                    urlSeller = f'{self.base_url}{soup.html.body.find("div", attrs={"class": "seller-info-name"}).find("a")["href"]}'
                except TypeError:
                    urlSeller = None
                params = [tuple(itm.text.split(':')) for itm in soupBody.findAll("li", attrs={"class":
                                                                                                  "item-params-list-item"})]
                result = {
                    'title': soup.head.title.text,
                    'price': float(price) if price else None,
                    'seller': seller,
                    'urlSeller': urlSeller,
                    'url': response.url,
                    'params': params
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
    catalog = ParseAvito('https://www.avito.ru/rossiya/kvartiry?cd=1')
    # t=catalog.get_urlPagination()
    catalog.insert_database()

