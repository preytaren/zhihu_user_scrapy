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
        item['approve'] = response.xpath("//div[@class='IconGraf']/text()").extract()[0].split(' ')[1]
        item['thanks'], item['collections'] = self.NUMBER_PATTERN.findall(''.join(response.xpath("//div[@class='Profile-sideColumnItemValue']/text()").extract()))
        item['following'], item['follower'] = response.xpath("//div[@class='NumberBoard-value']/text()").extract()
        item['anwsers'] = response.xpath("//a[@href='/people/{}/answers']/span/text()".format(response.url.split('/')[-1])).extract()[0]
        return item


    def parse_following_link(self, response):
        self.log('--- Parse following-link {} ---'.format(response.url))
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