# -*- coding: utf-8 -*-
import scrapy


class VkSpider(scrapy.Spider):
    name = 'vk'
    allowed_domains = ['vk.com']
    start_urls = ['http://vk.com/']

    def parse(self, response):
        pass
