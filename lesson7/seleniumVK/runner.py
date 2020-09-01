import os
from os.path import join, dirname
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from seleniumVK import settings
from seleniumVK.spiders.vk import VkSpider

do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

VK_login = os.getenv('VK_login')
VK_PSWRD = os.getenv('VK_PSWRD')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(VkSpider, VK_login, VK_PSWRD)
    process.start()
