# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymongo
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem

class Image360Pipeline(object):
    def process_item(self, item, spider):
        return item

# 保存到mongoDB
class MongoPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        collection = self.db[item.collection]
        collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()

# 保存到mysql
class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get(' MYSQL_DATABASE'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            user=crawler.settings.get('MYSQL_USER'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        # self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.database, port=self.port, charset='utf8')
        self.db = pymysql.connect(host=self.host, user=self.user, db=self.database,
                                  port=self.port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s']*len(data))
        sql = 'insert into %s (%s) values(%s)' %(item.table, keys, values)
        print(sql)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('ImageDownload Failed')
        return item

    def get_media_requests(self, item, info):
        yield Request(item['url'])