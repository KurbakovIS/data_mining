# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from parseAvito.items import ParseavitoItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/rossiya/vakansii?q=js']

    def parse(self, response: HtmlResponse):
        vacancy_urls = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        next_page = response.xpath('//a[@class="pagination-page"]/@href').extract_first()

        yield response.follow(next_page, callback=self.parse)
        for vac in vacancy_urls:
            yield response.follow(vac, callback=self.parse_vanacsy)

    def parse_vanacsy(self, response: HtmlResponse):
        name = response.xpath('//h1[@class="title-info-title"]/span/text()').extract_first()
        salary_cur = list(
            set(response.xpath('//span[@class="price-value-string js-price-value-string"]/span/@content').extract()))
        salary = {'currency': salary_cur[1] if salary_cur else None,
                  'min_value': salary_cur[0] if salary_cur else None
                  }
        yield ParseavitoItem(name=name, salary=salary)
