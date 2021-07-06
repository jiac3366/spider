# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from scrapy.http import Request
from articalspider.items import ArticalspiderItem
import re
import os
import time
import pickle
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from articalspider.settings import BASE_DIR


# 更好的抓取模式:不要写死‘100’页 翻页的时候根据next按键进行下一页的请求
# 创建项目 scrapy startproject [project_name]
# 生成命令：scrapy genspider cnblogs news.cnblogs.com
# 运行爬虫的命令: 直接debug main.py
# 测试scrapy: scrapy shell [url]
class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/n/697539/']  # 源码级分析：默认yield出url是start_urls中元素的请求 callback默认是parse()

    def __init__(self):
        # 为了防止每生成一个请求 就启动一个Chrome 所以把初始化Chrome放到每个爬虫的__init__()中 而不是放在中间件的process_request()
        self.browser = webdriver.Chrome(executable_path=r"E:\driver\chromedriver_win32\chromedriver.exe")
        super(CnblogsSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        """selenium获取cookie"""
        login_success = False
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

        if not cookies:
            self.browser.get('https://account.cnblogs.com/')
            time.sleep(3)
            self.browser.find_element_by_css_selector("#mat-input-0").send_keys('cjx463045792@163.com')
            self.browser.find_element_by_css_selector("#mat-input-1").send_keys('cjx1860750331')
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
                cookie_dict = {}
                for cookie in cookies:
                    cookie_dict[cookie['name']] = cookie['value']
                return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
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
        # post_node = response.xpath("//div[@id='news_list']/div[@class='news_block']")
        # for node in post_node:
        #     img_url = node.xpath(".//div[@class='entry_summary']/a/img/@src").extract_first("")
        #     post_url = node.xpath(".//h2[@class='news_entry']/a/@href").extract_first("")
        #     yield Request(url=parse.urljoin(response.url, post_url),
        #                   meta={"img_url": img_url},
        #                   callback=self.parse_detail)
        # # 2、提取下一页
        # next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

        # =====================以下是测试代码1===============================
        # node = response.xpath("//div[@id='news_list']/div[@class='news_block']")[0]
        # img_url = node.xpath(".//div[@class='entry_summary']/a/img/@src").extract_first("")
        # post_url = node.xpath(".//h2[@class='news_entry']/a/@href").extract_first("")
        # yield Request(url=parse.urljoin(response.url, post_url),
        #               meta={"img_url": img_url},
        #               callback=self.parse_detail)
        # pass
        # =====================以上是测试代码===============================

        # =====================以下是测试代码2===============================
        article_item = ArticalspiderItem()
        title = response.css("#news_title a::text").extract_first("")
        # title = response.xpath('//*[@id="news_title"]//a/text()')
        create_data = response.css("#news_info .time::text").extract_first("")
        match_re = re.match(".*?(\d+.*)", create_data)
        if match_re:
            create_date = match_re.group(1)
            # create_date = response.xpath('//*[@id="news_info"]//*[@class="time"]/text()')
        content = response.css("#news_content").extract()[0]
        # content = response.xpath('//*[@id="news_content"]').extract()[0]
        tag_list = response.css(".news_tags a::text").extract()
        # tag_list = response.xpath('//*[@class="news_tags"]//a/text()').extract()
        tags = ",".join(tag_list)
        pass
        # =====================以上是测试代码===============================

    def parse_detail(self, response):
        # ==详情页面字段过多，如何将数据进行传递呢？
        # ??因为博客园做了反爬 现在详情页好像不能直接访问到内容
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            print(match_re.groups(1))
            print(response.text)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()  # 目前无法关闭..
