# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuUserScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    url_name = scrapy.Field()
    area = scrapy.Field()
    education = scrapy.Field()
    approve = scrapy.Field()
    thanks = scrapy.Field()
    collections = scrapy.Field()
    anwsers = scrapy.Field()
    questions = scrapy.Field()
    following = scrapy.Field()
    follower = scrapy.Field()
