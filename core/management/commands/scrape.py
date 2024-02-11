from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class Command(BaseCommand):
    help = 'Run a Scrapy spider'

    def add_arguments(self, parser):
        parser.add_argument('spider_name', type=str, help='The name of the spider to run')

    def handle(self, *args, **options):
        spider_name = options['spider_name']

        # Setting up the CrawlerProcess with Scrapy settings
        process = CrawlerProcess(get_project_settings())

        # Dynamically importing the spider class based on spider_name
        spider_module = __import__(f"core.scrapy_project.spiders.{spider_name}", fromlist=[''])
        spider_class = getattr(spider_module, 'ProvidersSpider')  # Assuming a consistent naming convention

        # Starting the spider
        process.crawl(spider_class)
        process.start()

