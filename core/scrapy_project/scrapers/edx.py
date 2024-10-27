import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from .base_scraper import BaseScraper
from scrapy.spiders import SitemapSpider

# Improvements:
# Dynamically set the language based on the written out language on the website then get the iso code from that 
# Check Archived courses: https://www.edx.org/learn/social-science/mcgill-social-learning-for-social-impact

class EdxScraper(BaseScraper, SitemapSpider):
    name = 'edx_scraper'
    base_url = 'https://www.edx.org'
    sitemap_urls = [ base_url + '/sitemap-0.xml']

    # Constants
    IS_FREE = False
    IS_LIMITED_FREE = True
    LANGUAGE = ['en']
    

    def __init__(self, platform_id=None, *args, **kwargs):
        BaseScraper.__init__(self, platform_id, *args, **kwargs)
        SitemapSpider.__init__(self, *args, **kwargs)

    def sitemap_filter(self, entries):
        # Invalid: A url with only one '/' after the learn is a category page e.g. https://www.edx.org/learn/media-law
        # Invalid: A url with something else than learn after the base_url is an invalid url e.g. https://www.edx.org/certificates/professional-certificate/ucsandiegox-virtual-reality-app-development
        # Invalid: A two letter language iso code after the base is invalid for now e.g. https://www.edx.org/es/certificates/professional-certificate/ucsandiegox-virtual-reality-app-development
        # Valid: A url with 3 or more '/' after the base_url is a course e.g. https://www.edx.org/learn/statistics/university-of-adelaide-mathtrackx-statistics

        for entry in entries:
            url = entry['loc']
            
            pattern = rf'^{re.escape(self.base_url)}/learn/[^/]+/[^/]+$'
            if re.match(pattern, url):
                yield entry

    def start_requests(self):
        # Explicitly call SitemapSpider's start_requests method
        return SitemapSpider.start_requests(self)

    def parse(self, response):
        course_data = {
            'time_stamp': datetime.now().isoformat(),
            'platform': self.platform_id,
            'platform_course_id': self.extract_course_id(response),
            'url': response.url,
            'name': self.extract_name(response),
            'description': self.extract_description(response),
            'language': self.LANGUAGE,
            'is_free': self.IS_FREE,
            'is_limited_free': self.IS_LIMITED_FREE,
            'dollar_price': None,
            'has_certificate': None,
            'certificate_dollar_price': None,
            'creators': [],
            'format': None,
            'tags': [],
            'platform_last_mod': None,
            'platform_thumbnail_url': None,
            'duration': None,
            'reviews_count': None,
            'reviews_rating': None,
            'level': None,
        }
        print(course_data)

    def extract_course_id(self, response):
        enroll_url = response.css('a.btn.btn-brand.w-100::attr(href)').get()
        if enroll_url:
            parsed_url = urlparse(enroll_url)
            query_params = parse_qs(parsed_url.query)
            course_id = query_params.get('course_id', [None])[0]
            return course_id
        return response.url

    def extract_name(self, response):
        return response.css('h1::text').get().strip()

    def extract_description(self, response):
        text_content = " ".join(response.css('div.mt-2.lead-sm.html-data *::text').getall())
        return text_content.replace("\n", " ").strip()
