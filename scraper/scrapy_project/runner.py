from typing import Type
import crochet
from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings

# Initialize crochet only once
crochet.setup()

class ScrapyRunner:
    def __init__(self):
        self.settings = get_project_settings()
        # Ensure we don't try to manage the reactor
        self.settings.set('TWISTED_REACTOR_MANAGE', False)
        self.crawler = CrawlerRunner(self.settings)

    @crochet.wait_for(timeout=3600)
    def crawl(self, spider_cls: Type[Spider], *args, **kwargs):
        """Run the spider with proper cleanup"""
        try:
            return self.crawler.crawl(spider_cls, *args, **kwargs)
        except Exception as e:
            print(f"Error starting crawler: {e}")
            raise

    def stop(self):
        """Stop the crawler and cleanup"""
        # We don't need to manually stop the reactor as Crochet handles it
        pass 