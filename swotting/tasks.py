from huey import crontab
from huey.contrib.djhuey import task, db_task
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

@db_task()
def run_scraper(spider_name: str) -> str:
    """
    Run a single scraper
    
    Args:
        spider_name: Name of the spider to run (e.g., 'edx', 'coursera')
    """
    try:
        logger.info(f"Running {spider_name} scraper...")
        result = subprocess.run(
            ['python', 'manage.py', 'scrape', spider_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stderr:
            logger.warning(f"{spider_name} stderr: {result.stderr}")
            
        return f"{spider_name} scraping completed successfully"
        
    except subprocess.CalledProcessError as e:
        error_message = f"{spider_name} scraper failed: {e.stderr}"
        logger.error(error_message)
        raise Exception(error_message)

@task()
def run_all_scrapers() -> List[str]:
    """
    Run all scrapers sequentially
    """
    spider_names = ['edx']
    results = []
    
    for spider in spider_names:
        result = run_scraper(spider)
        results.append(result)
    
    return results
