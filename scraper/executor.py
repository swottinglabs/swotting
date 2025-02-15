import importlib
import json
import logging
import os
import tempfile
from django.conf import settings
from django.utils.timezone import now
from scrapy.crawler import Crawler, CrawlerProcess, CrawlerRunner
from scrapy.utils.spider import iter_spider_classes
from scraper.models import Spider as SpiderModel, Execution, Item
from typing import Optional, List, Dict, Any
from .logging import SpiderExecutionLogger
from .statistics import SpiderStatisticsManager
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy import signals
from asgiref.sync import sync_to_async
import signal
from scrapy.utils.defer import deferred_to_future
from crochet import setup, wait_for

logger = logging.getLogger(__name__)


class SpiderExecutor:
    """Core spider execution logic used by both direct calls and Celery tasks"""
    def __init__(self, spider_model):
        self.spider = spider_model
        self.logger = SpiderExecutionLogger(spider_model.name)
        self.stats_manager = SpiderStatisticsManager()
        self.settings = self._prepare_settings()
        self.execution = None

    def _prepare_settings(self):
        base_settings = get_project_settings()
        spider_settings = self.spider.settings or {}
        base_settings.update(spider_settings)
        return base_settings

    def execute(self):
        """Main execution method"""
        try:
            # Setup logging
            log_capture_string, handlers = self.logger.setup_logging()
            
            # Create execution record
            self.execution = Execution.objects.create(
                spider=self.spider,
                time_started=now()
            )

            # Load spider class
            spider_class = self._get_spider_class()
            
            # Initialize crawler
            runner = CrawlerRunner(self.settings)
            
            # Setup spider parameters
            spider_kwargs = {
                'name': self.spider.name.lower(),
                'platform_id': self.spider.name.lower(),
                'execution_id': self.execution.id,
                'stats_manager': self.stats_manager,
                'settings': self.spider.settings,
                'log_level': self.spider.log_level
            }

            # Run spider using crochet to handle the reactor
            setup()  # Initialize crochet
            
            @wait_for(timeout=3600)
            def run_spider():
                return runner.crawl(spider_class, **spider_kwargs)
            
            # Execute and wait
            run_spider()
            
            return {
                'status': 'success',
                'execution_id': self.execution.id,
                'items_scraped': self.stats_manager.get_stat('items_scraped')
            }

        except Exception as e:
            logger.error(f"Spider execution failed: {str(e)}", exc_info=True)
            raise

    def create_crawler(self, spider_class):
        """Create a crawler instance"""
        # Use the runner's create_crawler method directly
        crawler = self.runner.create_crawler(spider_class)
        
        # Connect signals
        crawler.signals.connect(self._item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self._spider_error, signal=signals.spider_error)
        crawler.signals.connect(self._spider_closed, signal=signals.spider_closed)
        
        return crawler
    
    def _item_scraped(self, item, response, spider):
        """Handle scraped item signal"""
        self.stats_manager.increment_stat('items_scraped')
        logger.info(f"Scraped item from {response.url}")

    def _spider_error(self, failure, response, spider):
        """Handle spider error signal"""
        self.stats_manager.increment_stat('errors')
        logger.error(f"Spider error on {response.url}: {failure.value}")

    def _spider_closed(self, spider, reason):
        """Handle spider closed signal"""
        logger.info(f"Spider {spider.name} closed: {reason}")
        logger.info(f"Final stats: {spider.crawler.stats.get_stats()}")
        self.stats_manager.set_stat('end_time', now())

    async def process_results(self, execution_result: Any) -> None:
        """Process the results of the spider execution"""
        await sync_to_async(self._process_results_sync)(execution_result)

    def _process_results_sync(self, execution: Execution) -> None:
        """Process the results of the spider execution"""
        if execution.items_scraped == 0:
            self._handle_zero_items()
            return

        self._check_execution_health(execution)

    def _setup_temp_storage(self):
        """Create temporary storage for spider output"""
        return tempfile.NamedTemporaryFile(
            prefix=f"spider_{self.spider.name}_",
            suffix='.jl',
            delete=False
        )

    def _get_spider_class(self):
        """Import and return the spider class"""
        try:
            module_path = self.spider.module.replace('/', '.').rstrip('.py')
            if module_path.startswith('.'):
                module_path = module_path[1:]
            
            logger.info(f"Attempting to import module: {module_path}")
            module = importlib.import_module(module_path)
            
            for cls in iter_spider_classes(module):
                logger.info(f"Found spider class: {cls.__name__}")
                return cls
            
            raise RuntimeError(f'No spider class found in {module_path}')
            
        except ImportError as e:
            logger.error(f"Import error for {module_path}: {str(e)}")
            raise

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
            logger.warning(f'Spider {self.spider.name} returned 0 items')

    def _check_execution_health(self, execution: Execution):
        """Check the health of the execution"""
        from .tasks import calculate_execution_average, check_spider_health
        
        executions = (Execution.objects
                     .filter(spider=self.spider)
                     .filter(time_ended__isnull=False)
                     .order_by('-time_ended'))[:4]

        if len(executions) >= 4:
            avg, msg = calculate_execution_average(executions, execution.items_scraped)
            if msg:
                logger.info(msg)
            
            status, health_msg = check_spider_health(self.spider, execution.items_scraped, avg)
            if health_msg:
                logger.info(health_msg)
            
            if status == "faulty":
                self.spider.faulty = True
                self.spider.save()

    def _handle_sigterm(self, signum, frame):
        """Handle termination signals gracefully"""
        logger.info("Received shutdown signal, stopping reactor...")
        try:
            if reactor.running:
                reactor.callFromThread(reactor.stop)
        except Exception as e:
            logger.error(f"Error stopping reactor: {e}")

    def cleanup(self):
        """Cleanup resources"""
        try:
            if reactor.running:
                reactor.callFromThread(reactor.stop)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            # Force cleanup if needed
            if reactor.running:
                try:
                    reactor._stopReactor()
                except:
                    pass


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
