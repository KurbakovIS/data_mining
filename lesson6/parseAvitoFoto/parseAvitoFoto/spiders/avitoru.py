# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from parseAvitoFoto.items import ParseavitofotoItem


class AvitoruSpider(scrapy.Spider):
    name = 'avitoru'
    allowed_domains = ['avito.ru']
    start_urls = ['http://avito.ru/rossiya/kvartiry']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)


    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=ParseavitofotoItem(), response=response)
        loader.add_xpath('photos',
                         '//div[contains(@class,"gallery-img-wrapper")]//div[contains(@class,"gallery-img-frame")]/img/@src')
        loader.add_xpath('title', '//h1[contains(@class,"title-info-title")]/span/text()')
        loader.add_xpath('params', '//li[contains(@class,"item-params-list-item")]')
        yield loader.load_item()
