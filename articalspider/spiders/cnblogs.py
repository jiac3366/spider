# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from scrapy.http import Request
from articalspider.items import ArticalspiderItem, ArticleItemLoader
import re
import os
import time
import json
import requests
import pickle
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from articalspider.settings import BASE_DIR
from articalspider.utils.comm import get_md5
from scrapy.loader import ItemLoader  # 并不是所有字段都需要ItemLoader来做


# 更好的抓取模式:不要写死‘100’页 翻页的时候根据next按键进行下一页的请求
# 创建项目 scrapy startproject [project_name]
# 生成命令：scrapy genspider cnblogs news.cnblogs.com
# 运行爬虫的命令: 直接debug main.py
# 测试scrapy: scrapy shell [url]
class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    # 源码级分析：默认yield出url是start_urls中元素的请求 callback默认是parse()
    start_urls = ['https://news.cnblogs.com']

    # start_urls = ['https://news.cnblogs.com/n/697539/']

    def __init__(self):
        # 为了防止每生成一个请求 就启动一个Chrome 所以把初始化Chrome放到每个爬虫的__init__()中 而不是放在中间件的process_request()
        self.browser = webdriver.Chrome(executable_path=r"E:\driver\chromedriver_win32\chromedriver.exe")
        self.login_name = 'cjx463045792@163.com'
        self.pwd = 'cjx1860750331'
        super(CnblogsSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        """selenium获取cookie"""
        try:
            self.browser.maximize_window()  # 将窗口最大化防止定位错误
        except:
            pass
        # 从文件中读取cookie
        cookies = []
        if os.path.exists(BASE_DIR + "/cookies/cnblogs.cookie"):
            cookies = pickle.load(open(BASE_DIR + "\\cookies\\cnblogs.cookie", "rb"))
            # for cookie in cookies:
            #     self.browser.add_cookie(cookie)
            # self.browser.get(self.start_urls[0])

        # 待完善：不仅仅需要检测是否有cookie 还要检测cookie是否过期
        if not cookies:
            print('no cookie')
            self.browser.get('https://account.cnblogs.com/')
            time.sleep(3)
            self.browser.find_element_by_css_selector("#mat-input-0").send_keys(self.login_name)
            self.browser.find_element_by_css_selector("#mat-input-1").send_keys(self.pwd)
            self.browser.find_element_by_css_selector(
                ".action-button.ng-tns-c139-2.mat-flat-button.mat-button-base.mat-primary").click()
            time.sleep(15)

            # my_blog = self.browser.find_element_by_xpath("//a[contains(text(),'我的博客')]")
            bling = self.browser.find_element_by_css_selector("#mat-badge-content-0")
            # is_success = bling or my_blog
            if bling:
                cookies = self.browser.get_cookies()
                print(cookies)
                # 写入cookie
                pickle.dump(cookies, open(BASE_DIR + "\\cookies\\cnblogs.cookie", "wb"))
            else:
                print("登录失败！")
                return

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse(self, response):
        """:parse()一般是写抓取策略的
        1、抽取详情页/列表图片的url
        2、抽取下一页的链接
        """
        # 1、
        # ==response.xpath('xxxx') 返回的是1个SelectorList 里面的Selector的root中是我们想要内容的属性
        # ==我们可以使用extract()抽取出来 extract()返回的也是List List装着想要的内容
        # extract_first("")可以返回这个List的第一个元素 ""是默认值
        post_node = response.xpath("//div[@id='news_list']/div[@class='news_block']")
        for node in post_node:
            img_url = node.xpath(".//div[@class='entry_summary']/a/img/@src").extract_first("")
            if img_url.startswith("//"):
                img_url = 'https:' + img_url
            post_url = node.xpath(".//h2[@class='news_entry']/a/@href").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"img_url": img_url},
                          callback=self.parse_detail)
        # 2、提取下一页
        next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # ==详情页面字段过多，如何将数据进行传递呢？
        # ??因为博客园做了反爬 现在详情页好像不能直接访问到内容
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)
            #     article_item = ArticalspiderItem()
            #     title = response.css("#news_title a::text").extract_first("")
            #     # title = response.xpath('//*[@id="news_title"]//a/text()')
            #     create_data = response.css("#news_info .time::text").extract_first("")
            #     match_time = re.match(".*?(\d+.*)", create_data)
            #     create_date = ''
            #     if match_time:
            #         create_date = match_time.group(1)
            #         # create_date = response.xpath('//*[@id="news_info"]//*[@class="time"]/text()')
            #     content = response.css("#news_content").extract()[0]
            #     # content = response.xpath('//*[@id="news_content"]').extract()[0]
            #     tag_list = response.css(".news_tags a::text").extract()
            #     # tag_list = response.xpath('//*[@class="news_tags"]//a/text()').extract()
            #     tags = ",".join(tag_list)
            #
            #     article_item["title"] = title
            #     article_item["create_date"] = create_date
            #     article_item["content"] = content
            #     article_item["tags"] = tags
            #     article_item["url"] = response.url
            #     if response.meta.get("img_url", ""):
            #         # 对于图片下载的字段 要使用list类型
            #         article_item["front_image_url"] = [response.meta.get("img_url", "")]
            #     else:
            #         article_item["front_image_url"] = []
            #     post_id = match_re.group(1)

            # item_loader = ItemLoader(item=ArticalspiderItem(), response=response)
            # 使用官方ItemLoader 返回的article_item值是一个list 但只有1个元素
            # 若pipeline需要string保存进mysql 那么如何将list里面的元素提取出来呢？
            item_loader = ArticleItemLoader(item=ArticalspiderItem(), response=response)
            item_loader.add_css("title", "#news_title a::text")
            item_loader.add_css("create_date", "#news_info .time::text")
            item_loader.add_css("content", "#news_content")
            item_loader.add_css("tags", ".news_tags a::text")
            item_loader.add_value("url", response.url)
            if response.meta.get("front_image_url", []):
                # response.meta.get("front_image_url", []) 这里的[]不能写成 ''
                item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))
            # 这里抓取断点查看article_item 会显示MapCompose()处理后的结果
            article_item = item_loader.load_item()

            # response.url 等同response.request.url?
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": article_item, "url": response.url},
                          callback=self.parse_nums)

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        article_item = response.meta.get("article_item", "")

        praise_nums = j_data["DiggCount"]
        fav_nums = j_data["TotalView"]
        comment_nums = j_data["CommentCount"]

        article_item["praise_nums"] = praise_nums
        article_item["fav_nums"] = fav_nums
        article_item["comment_nums"] = comment_nums
        article_item["url_object_id"] = get_md5(article_item["url"])

        yield article_item

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()  # 目前无法关闭..
