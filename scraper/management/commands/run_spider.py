from django.core.management.base import BaseCommand
import crochet
from scraper.scrapy_project.spiders.edx import EdxSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import logging
import os
import datetime
import sys
from django.db import connections

# Helper function to print debug info to console
def print_debug(message):
    """Print debug messages to console"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"DEBUG [{timestamp}]: {message}")

print_debug(f"Spider debug initialized")
print_debug(f"Python version: {sys.version}")
print_debug(f"Current working directory: {os.getcwd()}")

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
        print_debug(f"DATABASE_URL environment: {db_url}")
        
        # Log actual connection settings
        db_settings = connections.databases.get('default')
        if db_settings:
            db_host = db_settings.get('HOST', 'unknown')
            db_port = db_settings.get('PORT', 'unknown')
            db_name = db_settings.get('NAME', 'unknown')
            msg = f"Database connection: HOST={db_host}, PORT={db_port}, NAME={db_name}"
            self.stdout.write(msg)
            print_debug(msg)
        else:
            msg = "Could not retrieve database connection settings"
            self.stdout.write(self.style.WARNING(msg))
            print_debug(f"WARNING: {msg}")
            
        # Configure Scrapy settings
        settings = get_project_settings()
        # Explicitly disable reactor management
        settings.set('TWISTED_REACTOR_MANAGE', False)
        
        # Set log level for Scrapy
        settings.set('LOG_LEVEL', 'DEBUG')
        
        # Create and return the crawler
        runner = CrawlerRunner(settings)
        self.stdout.write("Crawler initialized, starting spider...")
        print_debug("Crawler initialized, starting spider...")
        return runner.crawl(EdxSpider)

    def handle(self, *args, **options):
        self.stdout.write('Starting EdX spider...')
        print_debug(f"Starting EdX spider")
        
        # Check database connection before starting
        try:
            # Try a simple database query to verify connection
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                msg = f"Database connection test successful: {result}"
                self.stdout.write(self.style.SUCCESS(msg))
                print_debug(msg)
        except Exception as e:
            msg = f"Database connection test failed: {e}"
            self.stdout.write(self.style.ERROR(msg))
            print_debug(f"ERROR: {msg}")
            import traceback
            print_debug(f"Connection error traceback: {traceback.format_exc()}")
        
        try:
            # Run the spider and wait for it to complete
            self.stdout.write("Setting up crawler...")
            print_debug("Setting up crawler...")
            deferred = self.setup_crawler()
            self.stdout.write("Waiting for crawler to complete...")
            print_debug("Waiting for crawler to complete...")
            # Wait for the crawl to complete with a timeout
            deferred.wait(timeout=3600)
            msg = 'Spider completed successfully'
            self.stdout.write(self.style.SUCCESS(msg))
            print_debug(msg)
        except Exception as e:
            msg = f'Spider failed: {e}'
            self.stderr.write(self.style.ERROR(msg))
            print_debug(f"ERROR: {msg}")
            import traceback
            trace = traceback.format_exc()
            self.stderr.write(trace)
            print_debug(f"Spider error traceback: {trace}")
        finally:
            # No need to manually clean up, just let Crochet handle it
            self.stdout.write("Spider process finished")
            print_debug("Spider process finished") 