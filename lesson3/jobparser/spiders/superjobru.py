# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/buhgalteriya-finansy-audit/']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacancy = response.css('div.f-test-vacancy-item div._3syPg div._2g1F- a._1QIBo::attr(href)').extract()

        for link in vacancy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('h1._3mfro::text').extract_first()
        salary = ''
        for itm in response.css('span.PlM3e span::text').extract():
            itm.replace(u'\xa0', ' ')
            salary = salary + itm
        company = response.css('h2.PlM3e::text').extract_first()
        yield JobparserItem(name=name, salary=salary, company=company)
