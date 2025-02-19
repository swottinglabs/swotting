from typing import Type
import crochet
from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider
from twisted.internet import reactor

crochet.setup()

class ScrapyRunner:
    def __init__(self):
        self.crawler = CrawlerRunner()
        self._crawl_deferred = None

    def crawl(self, spider_cls: Type[Spider], *args, **kwargs):
        """Run the spider with proper cleanup"""
        try:
            self._crawl_deferred = self.crawler.crawl(spider_cls, *args, **kwargs)
            return self._crawl_deferred
        except Exception as e:
            print(f"Error starting crawler: {e}")
            self.stop()
            raise

    def stop(self):
        """Stop the crawler and cleanup"""
        if reactor.running:
            reactor.stop() 