from django.core.management.base import BaseCommand
import crochet
from scraper.scrapy_project.spiders.edx import EdxSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import logging
import os
from django.db import connections

# Initialize crochet once at module level
crochet.setup()

class Command(BaseCommand):
    help = 'Run the EdX spider with Crochet'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with additional logging',
        )

    @crochet.run_in_reactor
    def setup_crawler(self):
        """Setup the crawler in the reactor thread"""
        # Log database connection settings
        db_url = os.environ.get('DATABASE_URL', 'Not set in environment')
        self.stdout.write(f"DATABASE_URL environment: {db_url}")
        
        # Log actual connection settings
        db_settings = connections.databases.get('default')
        if db_settings:
            db_host = db_settings.get('HOST', 'unknown')
            db_port = db_settings.get('PORT', 'unknown')
            self.stdout.write(f"Database connection: HOST={db_host}, PORT={db_port}")
        else:
            self.stdout.write(self.style.WARNING("Could not retrieve database connection settings"))
            
        # Configure Scrapy settings
        settings = get_project_settings()
        # Explicitly disable reactor management
        settings.set('TWISTED_REACTOR_MANAGE', False)
        
        # Set log level for Scrapy
        settings.set('LOG_LEVEL', 'DEBUG')
        
        # Create and return the crawler
        runner = CrawlerRunner(settings)
        self.stdout.write("Crawler initialized, starting spider...")
        return runner.crawl(EdxSpider)

    def handle(self, *args, **options):
        self.stdout.write('Starting EdX spider...')
        
        # Check database connection before starting
        try:
            # Try a simple database query to verify connection
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f"Database connection test successful: {result}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Database connection test failed: {e}"))
        
        try:
            # Run the spider and wait for it to complete
            self.stdout.write("Setting up crawler...")
            deferred = self.setup_crawler()
            self.stdout.write("Waiting for crawler to complete...")
            # Wait for the crawl to complete with a timeout
            deferred.wait(timeout=3600)
            self.stdout.write(self.style.SUCCESS('Spider completed successfully'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Spider failed: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())
        finally:
            # No need to manually clean up, just let Crochet handle it
            self.stdout.write("Spider process finished") 