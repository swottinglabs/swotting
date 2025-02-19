import importlib
import json
import logging
import os
from django.conf import settings
from django.utils.timezone import now
from scrapy.crawler import CrawlerRunner
from scrapy.utils.spider import iter_spider_classes
from scraper.models import Spider as SpiderModel, Execution
from .logging import SpiderExecutionLogger
from .statistics import SpiderStatisticsManager
from scrapy.utils.project import get_project_settings
from scrapy import signals
from twisted.internet import reactor
import crochet

# Initialize crochet
crochet.setup()

logger = logging.getLogger(__name__)

class SpiderExecutor:
    def __init__(self, spider_model):
        self.spider = spider_model
        self.logger = SpiderExecutionLogger(spider_model.name)
        self.stats_manager = SpiderStatisticsManager()
        self.settings = self._prepare_settings()
        self.execution = None
        self.runner = CrawlerRunner(self.settings)

    def _prepare_settings(self):
        base_settings = get_project_settings()
        spider_settings = self.spider.settings or {}
        base_settings.update(spider_settings)
        return base_settings

    @crochet.wait_for(timeout=3600)
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
            
            # Setup spider parameters
            spider_kwargs = {
                'name': self.spider.name.lower(),
                'platform_id': self.spider.name.lower(),
                'execution_id': self.execution.id,
                'stats_manager': self.stats_manager,
                'settings': self.spider.settings,
                'log_level': self.spider.log_level
            }

            # Run spider
            deferred = self.runner.crawl(spider_class, **spider_kwargs)
            return deferred

        except Exception as e:
            logger.error(f"Spider execution failed: {str(e)}", exc_info=True)
            raise

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

    def _handle_sigterm(self, signum, frame):
        """Handle termination signals gracefully"""
        logger.info("Received shutdown signal, stopping crawler...")
        try:
            self.runner.stop()
        except Exception as e:
            logger.error(f"Error stopping crawler: {e}")
