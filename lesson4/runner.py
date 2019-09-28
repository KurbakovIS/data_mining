import os
from os.path import join, dirname
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagramParser import settings
from instagramParser.spiders.instagram import InstagramSpider

do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

INST_LOGIN = os.getenv('INST_LOGIN')
INST_PWD = os.getenv('INST_PSWRD')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, ['mizgireva_', 'geekbrains.ru'], INST_LOGIN, INST_PWD)
    process.start()
