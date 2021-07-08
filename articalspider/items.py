# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re

from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags


# def add_article(value):
#     # 会对传进来的列表中的每一个元素都处理：在结尾+"-body"
#     return value + "-body"
#
# def add_test(value):
#     return value + "-body"

def date_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "0000-00-00"


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class ArticalspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # input_processor = MapCompose(add_author, add_test), # 测试用
        output_processor=Identity()  # front_image_url需要list类型 改为默认的Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    # 查看数
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into article_spider(title, url, url_object_id, front_image_path, front_image_url, praise_nums, comment_nums,
            fav_nums, tags, content, create_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums), praise_nums=VALUES(praise_nums), comment_nums=VALUES(comment_nums)
        """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("front_image_path", ""),
            self.get("front_image_url", ""),
            self.get("praise_nums", 0),
            self.get("comment_nums", 0),
            self.get("fav_nums", 0),
            self.get("tags", ""),
            self.get("content", ""),
            self.get("create_date", "0000-00-00"),
        )

        return insert_sql, params


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


def remove_splash(value):
    # 去掉工作城市的斜线
    return value.replace("/", "")


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    # def get_insert_sql(self):
    #     insert_sql = """
    #         insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
    #         job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
    #         tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #         ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
    #     """
    #     params = (
    #         self.get("title", ""),
    #         self.get("url", ""),
    #         self.get("url_object_id", ""),
    #         self.get("salary", ""),
    #         self.get("job_city", ""),
    #         self.get("work_years", ""),
    #         self.get("degree_need", ""),
    #         self.get("job_type", ""),
    #         self.get("publish_time", "0000-00-00"),
    #         self.get("job_advantage", ""),
    #         self.get("job_desc", ""),
    #         self.get("job_addr", ""),
    #         self.get("company_name", ""),
    #         self.get("company_url", ""),
    #         self.get("job_addr", ""),
    #         self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
    #     )
    #
    #     return insert_sql, params
