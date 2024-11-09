from django.core.management.base import BaseCommand
from core.scrapers import run_platform_scraper
from core.models import Platform

class Command(BaseCommand):
    help = 'Run scrapers for all platforms with isScraping=True'

    def handle(self, *args, **options):
        platforms = Platform.objects.filter(isScraping=True)
        for platform in platforms:
            run_platform_scraper(platform.id)
        self.stdout.write(self.style.SUCCESS('Scraping tasks have been scheduled'))