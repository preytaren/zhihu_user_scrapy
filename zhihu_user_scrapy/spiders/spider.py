# -*- encoding=utf-8 -*-
import re
import json
from scrapy.spider import Spider
from scrapy.http import Request

from ..items import ZhihuUserScrapyItem


class ZhihuSpider(Spider):

    name = 'zhihu'
    allowed_domain = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/people/excited-vczh']
    NUMBER_PATTERN = re.compile('[0-9]+')
    THANKS_PATTERN = re.compile(ur'获得 ([0-9]+) 次感谢', re.U)
    COLLECTION_PATTERN = re.compile(ur'([0-9]+) 次收藏', re.U)

    def parse(self, response):
        yield self.parse_item(response)
        url_user = response.url.split('/')[-1]
        yield Request(url='https://www.zhihu.com/api/v4/members/{}/followees?include=data%5B*%5D.' \
                          'answer_count%2Carticles_count%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge' \
                          '%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'.format(url_user),
                      callback=self.parse_following_link)

    def parse_item(self, response):
        self.log('--- Parse Item of user {} ---'.format(response.url))
        # 获得个人资料
        item = ZhihuUserScrapyItem()
        item['url'] = response.url
        item['name'] = response.xpath("//span[@class='ProfileHeader-name']/text()").extract()[0]
        item['img'] = response.xpath("//img[@class='Avatar Avatar--large UserAvatar-inner']/@src").extract()[0]
        item['approve'] = self.check_exist(
            lambda: int(response.xpath("//div[@class='IconGraf']/text()").extract()[0].split(' ')[1])
        )
        item['thanks'] = self.check_exist(
            lambda: self.THANKS_PATTERN.findall(response.xpath("//div[@class='Profile-sideColumnItemValue']/text()").extract()[0])[0]
        )
        item['collections'] = self.check_exist(
            lambda: self.COLLECTION_PATTERN.findall(response.xpath("//div[@class='Profile-sideColumnItemValue']/text()").extract()[0])[0]
        )
        item['following'], item['follower'] = map(int, response.xpath("//div[@class='NumberBoard-value']/text()").extract())
        item['answers'] = int(response.xpath("//a[@href='/people/{}/answers']/span/text()".format(response.url.split('/')[-1])).extract()[0])
        return item

    def check_exist(self, function, default=0):
        try:

            result = function()
            return result
        except Exception as e:
            self.log(e)
            return default

    def parse_following_link(self, response):
        content = json.loads(response.text)
        for url_token in self._parse_url_token(content['data']):
            yield Request(url='https://www.zhihu.com/people/{}'.format(url_token),
                          callback=self.parse)
        if content['paging']['is_end']:
            yield
        else:
            yield Request(url=content['paging']['next'],
                          callback=self.parse_following_link)

    def _parse_url_token(self, items):
        for item in items:
            if item['url_token']:
                yield item['url_token']