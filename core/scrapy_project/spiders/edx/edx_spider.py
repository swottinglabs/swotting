from scrapy.spiders import SitemapSpider

class EdxSpider(SitemapSpider):
    name = 'edx'
    sitemap_urls = ['https://www.edx.org/sitemap-0.xml']
    sitemap_rules = [
        ('/learn/', 'parse_course'),
    ]

    def parse_course(self, response):
        # This function will be implemented later
        pass
