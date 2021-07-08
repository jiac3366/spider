# -*- coding: utf-8 -*-

# Scrapy settings for articalspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'articalspider'

SPIDER_MODULES = ['articalspider.spiders']
NEWSPIDER_MODULE = 'articalspider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'articalspider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 10
RANDOMIZE_DOWNLOAD_DELAY = True  # 使得DOWNLOAD_DELAY在{0.5~1.5倍之间随机}
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False  # request不会把cookie带进去
COOKIES_ENABLED = True  # 第一次获取的cookie会自动分给后续的所有request
COOKIES_DEGUB = True  #

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'articalspider.middlewares.ArticalspiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'articalspider.middlewares.RandomUserAgentMiddlware': 1,
    # 'articalspider.middlewares.RandomProxyMiddleware': 2, # 代理ip
    # 'articalspider.middlewares.JSPageMiddleware': 3, # selenium集成
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None
}
RANDOM_UA_TYPE = 'random'

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 加入articalspide的项目路径
sys.path.insert(0, os.path.join(BASE_DIR, 'articalspider'))

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'scrapy.pipelines.images.ImagesPipeline': 1,
    'articalspider.pipelines.ArticalImagePipeline': 1,  # 图片下载
    # 'articalspider.pipelines.JsonWithEncodingPipeline': 2,  # 保存成json文件
    # 'articalspider.pipelines.MysqlPipeline': 3,  # 保存到mysql数据库
    'articalspider.pipelines.MysqlTwistedPipline': 3,  # 异步保存到mysql数据库，还可以对不同的爬虫入库解耦
    # 'articalspider.pipelines.ArticalspiderPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True  # DOWNLOAD_DELAY = 3秒 -->3秒下载一次
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

IMAGES_URLS_FIELD = "front_image_url"
IMAGES_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

MYSQL_HOST = "127.0.0.1"
MYSQL_DBNAME = "article_spider"
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"

if __name__ == '__main__':
    print(IMAGES_STORE)
# os.path中有dirname、abspath、join
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(os.path.join(BASE_DIR, 'articalspider'))
