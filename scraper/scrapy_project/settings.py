# Scrapy settings for scrapy_project project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
import sys
import django.conf
import dotenv
from pathlib import Path

dotenv.load_dotenv()

# Get the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Add the root directory to the Python path
sys.path.insert(0, str(ROOT_DIR))

# Setting up Django's settings module name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swotting.settings')

# Only setup Django if it hasn't been setup already
import django
if not django.conf.settings.configured:
    django.setup()

BOT_NAME = "scrapy_project"

SPIDER_MODULES = ["scraper.scrapy_project.spiders"]
NEWSPIDER_MODULE = "scraper.scrapy_project.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "scrapy_project (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1  # 1 second delay between requests
RANDOMIZE_DOWNLOAD_DELAY = True  # Adds some randomization to be more polite
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "scrapy_project.middlewares.ScrapyProjectSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "scrapy_project.middlewares.ScrapyProjectDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.memusage.MemoryUsage': None,
    'scrapy.extensions.corestats.CoreStats': None,
    'scrapy.extensions.logstats.LogStats': None,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "scrapy_project.pipelines.ScrapyProjectPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    # Pre-process Validators
    'scraper.scrapy_project.pipelines.validators.pre_process_validator.PreProcessValidatorPipeline': 110,
    
    # Duplicate Filter
    'scraper.scrapy_project.pipelines.learning_resources.duplicate_filter.DuplicateFilterPipeline': 115,
    
    # Text Cleaning
    'scraper.scrapy_project.pipelines.learning_resources.clean_text.TextCleanerPipeline': 120,
    
    # Database Validation
    'scraper.scrapy_project.pipelines.validators.database_validator.DatabaseValidatorPipeline': 900,
    
    # Database Save (final step)
    'scraper.scrapy_project.pipelines.learning_resources.database_save.DatabaseSavePipeline': 950,
}

# Reactor and Threading Settings
TWISTED_REACTOR = None  # Let Crochet choose the reactor
REACTOR_THREADPOOL_MAXSIZE = 1
TWISTED_REACTOR_MANAGE = False  # Let Crochet handle the reactor lifecycle
CONCURRENT_REQUESTS = 1  # Reduce concurrent requests to minimum
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# Disable features that might interfere with Crochet
TELNETCONSOLE_ENABLED = False

# Disable signals we don't need
SIGNALS_ENABLED = False

# Basic feed settings
FEEDS = {
    '%(name)s.jl': {
        'format': 'jsonlines',
        'encoding': 'utf-8',
        'overwrite': True,
    }
}

# Configure cleanup and shutdown
CLOSESPIDER_TIMEOUT = 180  # 3 minutes timeout
CLOSESPIDER_ERRORCOUNT = 1  # Stop after first error

# Configure logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# Disable retry middleware
RETRY_ENABLED = False

# Configure retry and timeout settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
DOWNLOAD_TIMEOUT = 180

# Disable some features during shutdown
MEDIA_ALLOW_REDIRECTS = False
REDIRECT_MAX_TIMES = 1

# Configure item pipelines to close gracefully
ITEM_PIPELINE_CLOSE_TIMEOUT = 60  # seconds