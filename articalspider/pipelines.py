# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class ArticalspiderPipeline(object):
    def process_item(self, item, spider):
        # 这里的item是经过items.py设置好后 经过cnblog.py解析爬取后的post_item信息
        return item
