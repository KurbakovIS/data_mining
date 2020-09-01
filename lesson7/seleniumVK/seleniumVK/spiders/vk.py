# -*- coding: utf-8 -*-
import scrapy
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.events
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from seleniumVK.items import ParseVKItem


class VkSpider(scrapy.Spider):
    name = 'vk'
    allowed_domains = ['vk.com']
    start_urls = ['http://vk.com/']
    urlsTitleFoto = []
    chromedrvr = "C:\\Users\\Posi_\\Desktop\\data_mining\\chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedrvr
    href = []
    imgHref = []

    def __init__(self, login, pswrd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.pswrd = pswrd
        self.driver = webdriver.Chrome(self.chromedrvr)

    def parse(self, response: HtmlResponse):
        self.driver.get("https://vk.com/")

        wait = WebDriverWait(self.driver, 10)
        self.driver.implicitly_wait(20)

        email = self.driver.find_element_by_css_selector('#index_email')
        password = self.driver.find_element_by_css_selector('#index_pass')

        email.send_keys(self.login)
        password.send_keys(self.pswrd)

        self.driver.find_element_by_css_selector('#index_login_button').click()

        fr = wait.until(EC.element_to_be_clickable((By.ID, 'l_fr')))
        fr.click()

        pr = wait.until(EC.element_to_be_clickable((By.ID, 'l_pr')))
        pr.click()

        self.driver.find_element_by_css_selector('#profile_photo_link').click()
        url = self.driver.current_url

        albumName = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pv_album_name")))
        albumName.click()

        photos_row = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "photos_container")))
        photos_row_a = photos_row.find_elements_by_tag_name('a')

        for a in photos_row_a:
            self.href.append(a.get_attribute('href'))

        for link in self.href:
            yield self.get_urlImg(link, wait)

        # self.driver.close()

        yield scrapy.FormRequest(
            url,
            callback=self.parse_user,
        )

    def get_frand(self):
       pass

    def get_urlImg(self, link, wait):
        self.driver.get(link)
        div = wait.until(EC.presence_of_element_located((By.ID, "pv_photo")))
        img = div.find_element_by_tag_name('img')
        self.imgHref.append(img.get_attribute('src'))
        self.driver.back()

    def get_urlImg(self, link, wait):
        self.driver.get(link)
        div = wait.until(EC.presence_of_element_located((By.ID, "pv_photo")))
        img = div.find_element_by_tag_name('img')
        self.imgHref.append(img.get_attribute('src'))
        self.driver.back()

    def parse_user(self, response: HtmlResponse):
        loader = ItemLoader(item=ParseVKItem(), response=response)
        loader.add_xpath('name', '//h2[@class="page_name"]/text()')
        loader.add_value('photos', self.imgHref)

        drTest = response.xpath('//div[contains(@class,"profile_info_row")]/div/text()').extract_first()
        if 'День рождения' in drTest:
            dr = response.xpath(
                '//div[contains(@class,"profile_info_row")]/div[contains(@class,"labeled")]/a/text()').extract()
        yield loader.load_item()
