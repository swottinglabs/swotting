from django.core.management.base import BaseCommand
from scrapy.cmdline import execute

class Command(BaseCommand):
    help = "Release the spiders"

    def handle(self, *args, **options):
        execute(['scrapy', 'crawl', 'yourspidername'])
