# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import HtmlResponse
import json


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    def __init__(self, user_links, login, pswrd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_links = user_links
        self.login = login
        self.pswrd = pswrd
        self.query_hash = 'c76146de99bb02f6415203be841dd25a'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            'http://instagram.com/accounts/login/ajax/',
            method='POST',
            callback=self.parse_users,
            formdata={'username': self.login, 'password': self.pswrd},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_users(self, response: HtmlResponse):
        j_body = json.loads(response.body)
        if j_body.get('authenticated'):
            for user in self.user_links:
                yield response.follow(self.make_graphql_url(user),
                                      callback=self.parse_user,
                                      cb_kwargs={'user': user})

    def parse_user(self, response: HtmlResponse, user):
        pass

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def make_graphql_url(self, user_vars):
        result = '{url}query_hash={hash}&{variables}'.format(
            url=self.graphql_url, hash=self.query_hash,
            variables=user_vars
        )
        return result
