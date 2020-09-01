# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import MapCompose, TakeFirst
import scrapy


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


class ParseVKItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))


class SeleniumvkItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
