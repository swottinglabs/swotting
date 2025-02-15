from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from scraper.logging import SpiderExecutionLogger
from scraper.models import Spider as SpiderModel, Execution
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from crochet import setup, wait_for
from scrapy.signalmanager import dispatcher
from scrapy import signals
import importlib
import logging

from scraper.statistics import SpiderStatisticsManager
from scraper.executor import SpiderExecutor

# Initialize crochet for handling async operations
setup()
logger = get_task_logger(__name__)

@shared_task(bind=True)
def start_spiders(self):
    """Start all active spiders"""
    logger.info("Starting scheduled spider runs")
    for spider in SpiderModel.objects.filter(active=True):
        run_spider.delay(spider.id)
    return "Scheduled all active spiders"

@shared_task(
    bind=True,
    rate_limit='3/m',  # Limit to 3 spiders per minute
    max_retries=3,     # Retry failed spiders 3 times
    soft_time_limit=3600,  # 1 hour timeout
    acks_late=True  # Important for proper shutdown
)
def run_spider(self, spider_id):
    """Run a single spider using the SpiderExecutor"""
    try:
        spider_model = SpiderModel.objects.get(id=spider_id)
        executor = SpiderExecutor(spider_model)
        return executor.execute()
    except Exception as e:
        logger.error(f"Spider task failed: {str(e)}", exc_info=True)
        raise

