# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import codecs
import json
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors


class ArticalspiderPipeline(object):
    def process_item(self, item, spider):
        # 我们自己在items.py定义好item后
        # 设置对应value(value在spider中解析提取)
        # Scrapy会自动将item传递到pipeline
        return item


class ArticalImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_path' in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path

        # 这里一定要return 不然下一个pipeline收不到
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # ON DUPLICATE KEY UPDATE praise_nums=VALUES(praise_nums) 可以防止数据的主键冲突 当冲突出现 更新praise_nums字段
        insert_sql = """
            insert into article_spider(title, url, url_object_id, praise_nums)
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE praise_nums=VALUES(praise_nums)
        """
        param = (item.get("title", ""),
                 item.get("url", ""),
                 item.get("url_object_id", ""),
                 item.get("praise_nums", 0)
                 )
        self.cursor.execute(insert_sql, param)
        self.conn.commit()


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlTwistedPipline(object):
    """异步入MySQL"""

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
