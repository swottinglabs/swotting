import importlib
import json
import logging
import os
import tempfile
from django.conf import settings
from django.utils.timezone import now
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.spider import iter_spider_classes
from scratchy.models import Spider as SpiderModel, Execution, Item
from typing import Optional, List, Dict, Any
from .logging import SpiderExecutionLogger
from .statistics import SpiderStatisticsManager

scraping_logger = logging.getLogger(__name__)


class SpiderExecutor:
    def __init__(self, spider: SpiderModel):
        self.spider = spider
        self.logger = SpiderExecutionLogger(spider.name)
        self.stats_manager = SpiderStatisticsManager()
        
    def execute(self) -> Execution:
        """Execute the spider and return the execution record"""
        execution = Execution.objects.create(
            spider=self.spider,
            time_started=now()
        )
        
        item_storage = self._setup_temp_storage()
        scrapy_settings = self._prepare_settings(item_storage.name)
        scrapy_spider_cls = self._get_spider_class()
        
        process = CrawlerProcess(settings=None, install_root_handler=False)
        log_capture_string, log_handler = self.logger.setup_logging()
        spider_logger = logging.getLogger(scrapy_spider_cls.name)
        spider_logger.addHandler(log_handler)
        
        crawler = Crawler(scrapy_spider_cls, scrapy_settings)
        process.crawl(crawler)
        process.start()
        
        # Capture results
        log_contents = log_capture_string.getvalue()
        self.logger.cleanup_logging(log_handler, spider_logger)
        
        # Update execution record
        execution.time_ended = now()
        execution.stats = crawler.stats._stats
        execution.log = log_contents
        execution.save()
        
        # Process items
        items = self._process_items(item_storage, execution)
        execution.items_scraped = len(items)
        execution.save()
        
        # Cleanup
        item_storage.close()
        os.remove(item_storage.name)
        
        return execution

    def process_results(self, execution: Execution):
        """Process execution results and update spider status"""
        if execution.items_scraped == 0:
            self._handle_zero_items()
            return

        execution_list = (Execution.objects
                         .filter(spider=self.spider)
                         .filter(time_ended__isnull=False)
                         .order_by('-time_ended'))

        if len(execution_list) >= 4:
            avg, avg_message = calculate_execution_average(execution_list, execution.items_scraped)
            scraping_logger.info(avg_message)
            
            status, message = check_spider_health(self.spider, execution.items_scraped, avg)
            if message:
                scraping_logger.info(message)
            
            if status == "faulty":
                self.spider.faulty = True
                self.spider.save()

    def _setup_temp_storage(self):
        """Create temporary storage for spider output"""
        return tempfile.NamedTemporaryFile(delete=False)

    def _prepare_settings(self, feed_uri: str) -> dict:
        """Prepare scrapy settings with proper precedence"""
        user_settings = getattr(settings, 'SCRATCHY_SPIDERS', {})
        
        default_settings = {
            'DOWNLOAD_DELAY': 1.5,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 5,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
            'RETRY_ENABLED': True,
            'RETRY_TIMES': 3,
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 429],
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'ROBOTSTXT_OBEY': True,
            'HTTPERROR_ALLOWED_CODES': [404, 403],
            'DOWNLOAD_TIMEOUT': 180,
            'CLOSESPIDER_TIMEOUT': 7200,
            'CLOSESPIDER_ERRORCOUNT': 50,
        }

        internal_settings = {
            'FEED_FORMAT': 'jsonlines',
            'FEED_EXPORT_ENCODING': 'utf-8',
            'FEED_URI': feed_uri,
        }

        return {
            **default_settings,
            **user_settings,
            **self.spider.settings,
            **internal_settings,
        }

    def _get_spider_class(self):
        """Import and return the spider class"""
        module = importlib.import_module(self.spider.module)
        
        for cls in iter_spider_classes(module):
            return cls
            
        raise RuntimeError(f'No valid spider class found in module {self.spider.module}')

    def _process_items(self, item_storage, execution: Execution) -> List[Item]:
        """Process and save scraped items"""
        item_storage.seek(0)
        items = []
        
        for line in item_storage.readlines():
            item_data = json.loads(line)
            item = Item(
                spider=self.spider,
                execution=execution,
                data=item_data
            )
            items.append(item)
            
        Item.objects.bulk_create(items, batch_size=100)
        return items

    def _handle_zero_items(self):
        """Handle case when no items were scraped"""
        if not self.spider.faulty:
            self.spider.faulty = True
            self.spider.save()
            message = f'Spider {self.spider.name} returned 0 items. Marked as Faulty.'
            scraping_logger.info(message)


def calculate_execution_average(execution_list, items_scraped):
    """Calculate the average items scraped from previous executions."""
    if len(execution_list) < 4:
        return None, "Insufficient execution history"
    
    previous_counts = [
        execution_list[i].items_scraped or 0 
        for i in range(1, 4)
    ]
    
    if all(count == 0 for count in previous_counts):
        return items_scraped, "No history. Using current execution count"
        
    valid_counts = [count for count in previous_counts if count > 0]
    if not valid_counts:
        return 0, "No valid previous executions"
        
    avg = sum(valid_counts) / len(valid_counts)
    message = f"{len(valid_counts)}+ Executions {'+'.join(map(str, valid_counts))} / {len(valid_counts)} = {avg:.2f} vs {items_scraped}"
    return avg, message

def check_spider_health(spider, items_scraped, avg):
    """Evaluate spider health based on items scraped vs average."""
    if avg == 0:
        return "faulty", "Spider marked as faulty due to zero average items"
    
    performance_ratio = items_scraped / avg
    
    if performance_ratio < 0.7 and not spider.faulty:
        message = f"Spider {spider.name} under-performing with {items_scraped} items vs Avg of {avg:.2f}"
        if performance_ratio < 0.4:
            return "faulty", f"{message} - Marked as faulty"
        return "warning", message
        
    if performance_ratio > 1.3:
        return "improved", f"Spider {spider.name} increased items by >30% of Avg: {items_scraped} items vs {avg:.2f}"
    
    return "healthy", None
