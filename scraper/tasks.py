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
        execution_result = executor.execute()
        executor.process_results(execution_result)
    except Exception as e:
        logger.error(f"Error running spider {spider.name}: {str(e)}")
        raise

