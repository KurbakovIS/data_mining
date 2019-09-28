# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import HtmlResponse
import json
from urllib.parse import urljoin, urlencode
from copy import deepcopy
from instagramParser.items import InstagramparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    variables_base = {'fetch_mutual': 'false', "include_reel": 'true', "first": 100}
    followers = {}
    media = {}
    postObj = {}
    likes = {}

    def __init__(self, user_links, login, pswrd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_links = user_links
        self.login = login
        self.pswrd = pswrd
        self.query_hash = 'c76146de99bb02f6415203be841dd25a'
        self.query_hash_media = 'df16f80848b2de5a3ca9495d781f98df'
        self.query_hash_post = 'd5d763b1e2acf209d62d22d184488e57'

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
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user,
                                      cb_kwargs={'user': user})

    def parse_user(self, response: HtmlResponse, user):
        user_id = self.fetch_user_id(response.text, user)
        user_vars = deepcopy(self.variables_base)
        user_vars.update({'id': user_id})
        yield response.follow(self.make_graphql_url(self.query_hash_media, user_vars),
                              callback=self.parse_media,
                              cb_kwargs={'user_vars': user_vars, 'user': user})

    def parse_media(self, response: HtmlResponse, user_vars, user):
        data = json.loads(response.body)
        if not self.media.get(user):
            self.media[user] = {'media': data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges'),
                                'count': data.get('data').get('user').get('edge_owner_to_timeline_media').get('count')}
        else:
            self.media[user]['media'].extend(
                data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges'))

        if data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info').get('has_next_page'):
            user_vars.update(
                {'after': data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info').get(
                    'end_cursor')}
            )
            next_page = self.make_graphql_url(self.query_hash_media, user_vars)
            yield response.follow(next_page,
                                  callback=self.parse_media,
                                  cb_kwargs={'user_vars': user_vars, 'user': user})

        if self.media.get(user) and self.media.get(user).get('count') == len(self.media.get(user).get(
                'media')):
            data_media = self.media.get(user)
            user_vars_post = deepcopy(self.variables_base)
            for userPost in data_media.get('media')[:10]:
                shortcode = userPost.get('node').get('shortcode')
                user_vars_post.update({'shortcode': shortcode})

                name_post = userPost.get('node').get('edge_media_to_caption').get('edges')[0].get(
                    'node').get('text')
                comments_user = userPost.get('node').get('edge_media_to_comment').get('edges')

                self.parse_comment(comments_user, name_post)

                url_post_likes = self.make_graphql_url(self.query_hash_post, user_vars_post)
                yield response.follow(url_post_likes,
                                      callback=self.parse_post_like,
                                      cb_kwargs={
                                          'user_vars_post': user_vars_post,
                                          'name_post': name_post, 'user': user})

    def parse_comment(self, comments_user, name_post):
        for comment in comments_user:
            own_comment = {'id': comment.get('node').get('owner').get('id'),
                           'username': comment.get('node').get('owner').get('username'),
                           'profile_pic_url': comment.get('node').get('owner').get('profile_pic_url')}
            if not self.postObj.get(name_post):
                self.postObj[name_post] = {'comments': [own_comment], 'likes': []}
            else:
                self.postObj[name_post]['comments'].append(own_comment)

    def parse_post_like(self, response: HtmlResponse, user_vars_post, name_post, user):
        data = json.loads(response.body)
        like_list = data.get('data').get('shortcode_media').get('edge_liked_by').get('edges')

        if not self.likes.get(name_post):
            self.likes[name_post] = {'likes': like_list}
        else:
            self.likes[name_post]['likes'].append(like_list)

        if data.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get('has_next_page'):
            user_vars_post.update(
                {'after': data.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get(
                    'end_cursor')})
            next_page = self.make_graphql_url(self.query_hash_post, user_vars_post)
            yield response.follow(next_page,
                                  callback=self.parse_post_like,
                                  cb_kwargs={'user_vars_post': user_vars_post,
                                             'name_post': name_post, 'user': user})
        self.parse_like(name_post)

        name = user
        postComments = self.postObj[name_post]['comments']
        ownersLike = self.postObj[name_post]['likes']
        name_post = name_post
        yield InstagramparserItem(name=name,
                                  name_post=name_post,
                                  postComments=postComments,
                                  ownersLike=ownersLike)

    def parse_like(self, name_post):
        for likeName in self.likes:
            for like in self.likes[likeName].get('likes'):
                try:
                    node = like.get('node')
                except AttributeError:
                    node = like[0].get('node')

                self.postObj[name_post]['likes'].append({'owner_like_id': node.get('id'),
                                                         'owner_like_name': node.get('username'),
                                                         'owner_like_url': node.get('profile_pic_url')})

    def parse_folowers(self, response: HtmlResponse, user_vars, user):
        data = json.loads(response.body)
        if not self.followers.get(user):
            self.followers[user] = {'followers': data.get('data').get('user').get('edge_followed_by').get('edges'),
                                    'count': data.get('data').get('user').get('edge_followed_by').get('count')}
        else:
            self.followers[user]['followers'].extend(data.get('data').get('user').get('edge_followed_by').get('edges'))

        if data.get('data').get('user').get('edge_followed_by').get('page_info').get('has_next_page'):
            user_vars.update(
                {'after': data.get('data').get('user').get('edge_followed_by').get('page_info').get('end_cursor')}
            )
            next_page = self.make_graphql_url(self.query_hash, user_vars)
            yield response.follow(next_page,
                                  callback=self.parse_folowers,
                                  cb_kwargs={'user_vars': user_vars, 'user': user})
        if self.followers.get(user) and self.followers.get(user).get('count') == len(self.followers.get(user).get(
                'followers')):
            pass

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, query_hash, user_vars):
        result = '{url}query_hash={hash}&{variables}'.format(
            url=self.graphql_url, hash=query_hash,
            variables=urlencode(user_vars)
        )
        return result
