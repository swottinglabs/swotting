from django.core.management.base import BaseCommand
from scraper.scrapy_project.runner import ScrapyRunner
from scraper.scrapy_project.spiders.edx import EdxSpider

class Command(BaseCommand):
    help = 'Run the EdX spider'

    def handle(self, *args, **options):
        runner = ScrapyRunner()
        try:
            d = runner.crawl(EdxSpider)
            d.addBoth(lambda _: runner.stop())
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Spider failed: {e}'))
            runner.stop() 