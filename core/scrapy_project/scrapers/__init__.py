"""
Initialize scrapers package and expose spider classes
"""
from .edx import EdxScraper
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import Type
from .base_scraper import BaseScraper
from multiprocessing import Process

__all__ = ['EdxScraper']

def run_spider_in_process(spider_class: Type[BaseScraper], platform_id: str):
    """
    Run a spider in a separate process
    """
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_class, platform_id=platform_id)
    process.start()

def run_scraper(spider_class: Type[BaseScraper], platform_id: str) -> None:
    """
    Run a scraper in a separate process
    
    Args:
        spider_class: The spider class to run
        platform_id: The platform ID to scrape
    """
    # Create and start process
    process = Process(target=run_spider_in_process, args=(spider_class, platform_id))
    process.start()
    process.join()  # Wait for process to complete
