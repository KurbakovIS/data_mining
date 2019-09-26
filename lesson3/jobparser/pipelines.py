# -*- coding: utf-8 -*-

from database.base import VacancyDB
from database.models import Vacancy
from pymongo import MongoClient


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy
        self.sql_db = VacancyDB('sqlite:///vacancy.sqlite')

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        db_item = Vacancy(name=item.get('name'), spider=spider.name, salary=item.get('salary'),
                          company=item.get('company'))
        self.sql_db.add_salary(db_item)
        return item
