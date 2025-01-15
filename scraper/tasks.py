import importlib
import json
import logging
import os
import tempfile
from django.conf import settings
from django.utils.timezone import now
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.spider import iter_spider_classes
from scraper.executor import SpiderExecutor
from scraper.models import Spider as SpiderModel, Execution, Item
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task
from twisted.internet import reactor


logger = logging.getLogger(__name__)


@db_periodic_task(crontab(day_of_week='0', hour='0', minute='0')) # Runs weekly
def start_spiders():
    logger.info("Starting task 'Start Spiders' in scraper module")
    for spider in SpiderModel.objects.filter(active=True):
        run_spider(spider.id)


@db_task()
def run_spider(spider_id, processing_execution_id=None):
    spider = SpiderModel.objects.get(id=spider_id)
    executor = SpiderExecutor(spider)
    
    try:
        # Create a future to store the result
        future = {}
        
        def on_success(execution):
            future['result'] = execution
            
        def on_error(failure):
            future['error'] = failure
            logger.error(f"Spider failed: {failure.getErrorMessage()}")
            
        # Run the spider and wait for completion
        deferred = executor.execute()
        deferred.addCallbacks(on_success, on_error)
        
        # Let the reactor run until the spider is done
        while 'result' not in future and 'error' not in future:
            reactor.runUntilCurrent()
            
        if 'error' in future:
            raise Exception(str(future['error']))
            
        execution_result = future['result']
        executor.process_results(execution_result)
        
    except Exception as e:
        logger.error(f"Error running spider {spider.name}: {str(e)}")
        raise

