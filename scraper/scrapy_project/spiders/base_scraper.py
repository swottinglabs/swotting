import scrapy
from scrapy import signals


class BaseSpider(scrapy.Spider):
    name = 'base_scraper'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def __init__(self, platform_id, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.platform_id = platform_id

    def spider_closed(self, spider):
        """Cleanup method called when spider is closed"""
        self.logger.info('Spider closed: %s', spider.name)

    def start_requests(self):
        # Implement the logic to start scraping
        pass

    def parse(self, response):
        # Implement the parsing logic
        pass