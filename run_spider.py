#!/usr/bin/env python
"""
Custom spider runner script that properly handles the Twisted reactor
to avoid ReactorAlreadyRunning errors.
"""
import os
import sys
import django
import crochet

# Add current directory to path and setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swotting.settings")
django.setup()

# Start crochet and wrap the main function
crochet.setup()

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.scrapy_project.spiders.edx import EdxSpider

def run_spider(spider_name):
    """Run a spider safely using crochet to handle the reactor"""
    # Get the spider class based on name
    spider_classes = {
        'edx': EdxSpider,
    }
    
    if spider_name not in spider_classes:
        print(f"Spider '{spider_name}' not found. Available spiders: {', '.join(spider_classes.keys())}")
        return
    
    # Get settings and configure
    settings = get_project_settings()
    settings.set('TWISTED_REACTOR_MANAGE', False)
    
    # Initialize the crawler process
    process = CrawlerProcess(settings)
    
    # Add the spider and start crawling
    process.crawl(spider_classes[spider_name])
    
    # Use crochet to run the reactor in a controlled way
    @crochet.wait_for(timeout=3600)
    def _crawl():
        return process.join()
    
    try:
        _crawl()
        print(f"Spider '{spider_name}' completed successfully")
    except Exception as e:
        print(f"Spider '{spider_name}' failed: {e}")

if __name__ == "__main__":
    # Check if a spider name was provided
    if len(sys.argv) < 2:
        print("Usage: python run_spider.py [spider_name]")
        print("Available spiders: edx")
        sys.exit(1)
    
    spider_name = sys.argv[1]
    run_spider(spider_name) 