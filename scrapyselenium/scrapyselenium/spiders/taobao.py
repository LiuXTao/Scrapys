# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote
from scrapyselenium.items import ProductItem
from scrapy import Request

class TaobaoSpider(scrapy.Spider):
    name = "taobao"
    allowed_domains = ["www.taobao.com"]
    # start_urls = ['http://www.taobao.com/']
    base_url = 'https://s.taobao.com/search?&app=detailproduct&through=1&cps=yes&cd=false&v=auction&s=0&tab=all&q='

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword)
                yield Request(url=url, callback=self.parse, meta={'page': page}, dont_filter=True)

    def parse(self, response):
        products = response.css('#mainsrp-itemlist .items .item')
        for product in products:
            item = ProductItem()
            item['price'] = ''.join(product.css('.row .price *::text').extract()).strip()
            item['title'] = ''.join(product.css('.title *::text').extract()).strip()
            item['shop'] = ''.join(product.css('.row .shop .shopname *::text').extract()).strip()
            item['image'] = ''.join(product.css('.pic .img::attr("data-src")').extract()).strip()
            item['deal'] = product.css('.deal-cnt::text').extract_first()
            item['location'] = product.css('.location::text').extract_first()
            print(item['price'], item['title'], item['shop'])
            yield item
        # products = response.xpath(
        #     '//div[@id="mainsrp-itemlist"]//div[@class="items"][1]//div[contains(@class, "item")]')
        # for product in products:
        #     item = ProductItem()
        #     item['price'] = ''.join(product.xpath('.//div[contains(@class, "price")]//text()').extract()).strip()
        #     item['title'] = ''.join(product.xpath('.//div[contains(@class, "title")]//text()').extract()).strip()
        #     item['shop'] = ''.join(product.xpath('.//div[contains(@class, "shop")]//text()').extract()).strip()
        #     item['image'] = ''.join(
        #         product.xpath('.//div[@class="pic"]//img[contains(@class, "img")]/@data-src').extract()).strip()
        #     item['deal'] = product.xpath('.//div[contains(@class, "deal-cnt")]//text()').extract_first()
        #     item['location'] = product.xpath('.//div[contains(@class, "location")]//text()').extract_first()
        #     print(item['price'], item['title'], item['shop'])
        #     yield item

