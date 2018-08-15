# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlencode
from scrapy import Request
from scrapy import Spider

from image360.items import ImageItem


class ImageCrawlSpider(scrapy.Spider):
    name = "image_crawl"
    allowed_domains = ["images.so.com"]
    start_urls = ['http://images.so.com/']

    def start_requests(self):
        data = {'ch':'photography', 'listtype':'new'}
        base_url = 'https://image.so.com/zj?'
        for page in range(1, self.settings.get('MAX_PAGE')+1):
            data['sn'] = page*30
            params = urlencode(data)
            url = base_url + params
            yield Request(url, self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        image_list = result.get('list')
        for image in image_list:
            item = ImageItem()
            item['id'] = image.get('imageid')
            item['url'] = image.get('qhimg_url')
            item['title'] = image.get('group_title')
            item['thumb'] = image.get('qhing_thumb_url')
            yield item
