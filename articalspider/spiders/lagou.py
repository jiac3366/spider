# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
import time

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    # rules是一个可迭代的对象
    # 1、Rule类参数讲解：
    # callback是allow定义的url的回调函数 其中cb_kwargs是回调函数的参数 follow决定要不要对满足rule的url进行跟踪
    # process_link可以对需要的rul再加一层预处理
    # 2、LinkExtractor类参数讲解：
    # allow符合规则的url就提取 deny与allow相反 allow_domain也同理 restrict_xpaths固定提取页面某个位置的url(有可能其他位置也存在符合规定的url)
    # tag默认是a 和 area标签（不覆盖）restrict_css与restrict_xpaths同理
    # css（css可以处理HTML）最终都会转换为Xpath（Xpath可以处理XML）进行处理
    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    # 经过源码解析 可以得知start_requests()运行在最前
    def start_requests(self):
        browser = webdriver.Chrome(executable_path=r"E:\driver\chromedriver_win32\chromedriver.exe")
        browser.get('https://passport.lagou.com/login/login.html')
        time.sleep(3)
        browser.find_element_by_css_selector(".form_body input[type='text']").send_keys('463045792@qq.com')
        browser.find_element_by_css_selector(".form_body input[type='password']").send_keys('cjx1860750331')
        browser.find_element_by_css_selector(".form_body input[type='submit']").click()
        time.sleep(3)
        cookies = browser.get_cookies()
        print(cookies)



    # CrawlSpider源码分析： 不能覆盖parse()函数
    # 可以重载parse_start_url()
    def parse_job(self, response):
        item = {}
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()
        return item
