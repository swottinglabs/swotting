from huey import crontab
from huey.contrib.djhuey import periodic_task, task
from core.models import Platform
from core.scrapy_project.scrapers import run_platform_scraper

@task()
def run_scraper_task(platform_id):
    run_platform_scraper(platform_id)

@periodic_task(crontab(day='*/14'))
def biweekly_scraping_task():
    platforms = Platform.objects.filter(isScraping=True)
    for platform in platforms:
        run_scraper_task(platform.id)
