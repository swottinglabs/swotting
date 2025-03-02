from django.core.management.base import BaseCommand
import crochet
from scraper.scrapy_project.spiders.edx import EdxSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

# Initialize crochet once at module level
crochet.setup()

class Command(BaseCommand):
    help = 'Run the EdX spider with Crochet'

    @crochet.run_in_reactor
    def setup_crawler(self):
        """Setup the crawler in the reactor thread"""
        settings = get_project_settings()
        # Explicitly disable reactor management
        settings.set('TWISTED_REACTOR_MANAGE', False)
        runner = CrawlerRunner(settings)
        return runner.crawl(EdxSpider)

    def handle(self, *args, **options):
        self.stdout.write('Starting EdX spider...')
        try:
            # Run the spider and wait for it to complete
            deferred = self.setup_crawler()
            # Wait for the crawl to complete with a timeout
            deferred.wait(timeout=3600)
            self.stdout.write(self.style.SUCCESS('Spider completed successfully'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Spider failed: {e}'))
        finally:
            # No need to manually clean up, just let Crochet handle it
            pass 