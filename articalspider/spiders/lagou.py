# -*- coding: utf-8 -*-
import scrapy
import time
import pickle
import os
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from articalspider.settings import BASE_DIR
from articalspider.utils.comm import get_md5
from articalspider.items import LagouJobItemLoader, LagouJobItem

# tips:
# scrapy crawl xxx - s MONGODB_URI='mongodb://user:password@123.15.43.32:7766'
# 命令行用参数-s就可以覆盖setting.py中的设置
# 创建项目：scrapy genspider -t crawl 爬虫名
class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/zhaopin/']

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
        "Referer": 'https://www.lagou.com',
        'Connection': 'keep-alive',
        "Host": "www.lagou.com"
    }

    # rules是一个可迭代的对象
    # 1、Rule类参数讲解：
    # callback是allow定义的url的回调函数 其中cb_kwargs是回调函数的参数 follow决定要不要对满足rule的url进行跟踪
    # process_link可以对需要的rule再加一层预处理
    # 2、LinkExtractor类参数讲解：
    # allow符合规则的url就提取 deny与allow相反 allow_domain是对域名符合规则就处理
    # deny_domains也同理 restrict_xpaths固定提取页面某个位置的url(因为有可能其他位置也存在符合规定的url)
    # tag默认是a 和 area标签（不用覆盖这个参数）restrict_css与restrict_xpaths作用类似
    # css（css可以处理HTML）最终都会转换为Xpath（Xpath可以处理XML）进行处理
    rules = (
        # Rule(LinkExtractor(allow=("zhaopin/",)), follow=True),
        # Rule(LinkExtractor(allow=("gongsi/v1/j/\w+.html",)), follow=True),
        # 前2条rule的对应的url都可以跳转到职位信息 所以callback函数应该写在最后这一条url中
        Rule(LinkExtractor(allow=r'jobs/.*'), callback='parse_job', follow=True),
    )

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.browser = webdriver.Chrome(executable_path=r"E:\driver\chromedriver_win32\chromedriver.exe",
                                        options=options)
        super(LagouSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    # 经过源码解析 可以得知start_requests()运行在最前
    def start_requests(self):
        try:
            self.browser.maximize_window()  # 将窗口最大化防止定位错误
        except:
            pass

        cookies = []
        self.browser.get('https://www.lagou.com/')
        if os.path.exists(BASE_DIR + "/cookies/lagou.cookie"):
            cookies = pickle.load(open(BASE_DIR + "/cookies/lagou.cookie", "rb"))
            print(cookies)
            for cookie in cookies:
                self.browser.add_cookie(cookie)
            time.sleep(2)
            self.browser.get('https://www.lagou.com/zhaopin/')


        if not cookies:
            self.browser.get('https://passport.lagou.com/login/login.html')
            time.sleep(3)
            self.browser.find_element_by_css_selector(".form_body input[type='text']").send_keys('463045792@qq.com')
            self.browser.find_element_by_css_selector(".form_body input[type='password']").send_keys('cjx1860750331')
            self.browser.find_element_by_css_selector(".form_body input[type='submit']").click()
            time.sleep(12)
            cookies = self.browser.get_cookies()
            print(cookies)
            pickle.dump(cookies, open(BASE_DIR + "/cookies/lagou.cookie", "wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict, headers=self.headers)

    # CrawlSpider源码分析： 不能覆盖parse()函数
    # 可以重载parse_start_url()
    def parse_job(self, response):
        # 解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']//span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']//span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']//span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']//span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()

        return job_item

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()  # 目前无法关闭..
