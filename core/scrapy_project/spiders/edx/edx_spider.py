import os
from scrapy.spiders import SitemapSpider
from scrapy.exceptions import CloseSpider

class EdxSpider(SitemapSpider):
    name = 'edx'
    sitemap_urls = ['https://www.edx.org/sitemap-0.xml']
    sitemap_rules = [
        ('/learn/', 'parse_course'),
    ]

    def parse_course(self, response):
        # Save the response to a file
        filename = f'edx_response_{response.url.split("/")[-1]}.html'
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'wb') as f:
            f.write(response.body)
        
        self.logger.info(f'Saved file {filepath}')
        
        # Stop the spider
        raise CloseSpider('First URL processed')
