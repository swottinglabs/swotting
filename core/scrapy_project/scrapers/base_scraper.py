import scrapy

class BaseScraper(scrapy.Spider):
    name = 'base_scraper'

    def __init__(self, platform_id, *args, **kwargs):
        super(BaseScraper, self).__init__(*args, **kwargs)
        self.platform_id = platform_id

    def start_requests(self):
        # Implement the logic to start scraping
        pass

    def parse(self, response):
        # Implement the parsing logic
        pass
