# -*- encoding=utf-8 -*-
import re
from scrapy import log
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy_splash import SplashRequest

from ..items import ZhihuUserScrapyItem


class ZhihuSpider(Spider):

    name = 'zhihu'
    allowed_domain = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/people/excited-vczh']
    NUMBER_PATTERN = re.compile('[0-9]+')

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait':0.5})

    def parse(self, response):
        if response.url[-9:] == 'following':
            for link in self.parse_following_link(response):
                yield link
        else:
            for item in self.parse_user_link(response):
                yield item

    def parse_item(self, response):
        log.msg('Parse Item of user "{}"'.format(response.url))
        # 获得个人资料
        item = ZhihuUserScrapyItem()
        item.url = response.url
        item.name = response.xpath("//span[@class='ProfileHeader-name']/text()").extract()[0]
        item.approve = response.xpath("//div[@class='IconGraf']/text()").extract()[0].split(' ')[1]
        item.thanks, item.collections = self.NUMBER_PATTERN.findall(response.xpath("//div[@class='Profile-sideColumnItemValue']/text()").extract()[0])
        item.following, item.follower = response.xpath("//div[@class='NumberBoard-value']/text()").extract()
        item.anwsers = response.xpath("//a[@href='/people/{}/answers']/span/text()".format(response.url.split('/')[-1])).extract()[0]
        return item

    def parse_link(self, response):
        return (u'https://www.zhihu.com/{}'.format(url) \
                     for url in response.xpath("//a[@class='UserLink-link']/@href").extract())

    def parse_user_link(self, response):
        yield self.parse_item(response)
        user_name = response.url.split('/')[-2]
        yield SplashRequest(url='https://www.zhihu.com/people/{}/following'.format(user_name),
                            callback=self.parse_following_link,
                            args={'wait':0.5})

    def parse_following_link(self, response):
        for link in self.parse_link(response):
            yield SplashRequest(url=link,
                                callback=self.parse_user_link,
                                args={'wait': 0.5})