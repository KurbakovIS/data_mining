# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def create_params(values):
    params = {}
    data = values.split('>')
    param = data[2].split(':')[0]
    param_value = data[3].split(' ')[0]
    try:
        if int(param_value):
            param_value = int(param_value)
    except ValueError:
        if u'\xa0' in param_value:
            param_value = param_value.replace(u'\xa0', '')

    params[param] = param_value
    return params


class ParseavitofotoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    params = scrapy.Field(output_processor=MapCompose(create_params))


class ParseavitoItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
