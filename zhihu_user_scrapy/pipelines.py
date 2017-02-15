# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os.path
from sqlite3 import dbapi2 as sqlite

from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from scrapy.exceptions import DropItem

from tasks import download


Base = declarative_base()


class db_user(Base):
    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    url = Column(String(100))
    approve = Column(Integer)
    thanks = Column(Integer)
    collections = Column(Integer)
    answers = Column(Integer)
    following = Column(Integer)
    follower = Column(Integer)

    @classmethod
    def create_from_item(cls, item):
        return cls(name=item['name'],
                   url=item['url'],
                   approve=item['approve'],
                   thanks=item['thanks'],
                   collections=item['collections'],
                   answers=item['answers'],
                   following=item['following'],
                   follower=item['follower']
                   )


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['url'])
            return item


class SaveToDatabasePipeline(object):

    def __init__(self):
        self.engine = create_engine('sqlite+pysqlite:///zhihu_user.db', module=sqlite)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def process_item(self, item, spider):
        zhihu_user = db_user.create_from_item(item)
        self.session.add(zhihu_user)
        self.session.commit()
        return item

    def close_spider(self, spider):
        self.session.close()


class DownloadImagePipeline(object):

    def __init__(self):
        self.path = 'images'

    def process_item(self, item, spider):
        image_url = item['img']
        item['img'] = item['img'][item['img'].rfind('/')+1:]
        # post to Celery
        download.delay(image_url, os.path.join(os.path.dirname(os.path.abspath(item['img'])),
                                               'images'))
        spider.log('Downloaded {}'.format(image_url))
        return item