import json
from scrapy.spiders import SitemapSpider
from scrapy.http import Request
from core.scrapy_project.items import LearningResourceItem

class ProvidersSpider(SitemapSpider):
    name = 'edx_spider'
    sitemap_urls = ['https://www.edx.org/sitemap-0.xml']
    sitemap_rules = [
        ('/learn/', 'parse_course'),
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    }

    def sitemap_filter(self, entries):
        for entry in entries:
            url = entry['loc']
            if '/learn/' in url:
                # Convert the sitemap URL directly to the data URL
                data_url = f"https://www.edx.org/page-data{url[20:]}/page-data.json"
                yield Request(url=data_url, callback=self.parse_course)

    def parse_course(self, response):
        try:
            data = json.loads(response.text)
            course_info = data.get('result', {}).get('pageContext', {}).get('course', {})

            item = LearningResourceItem()
            item['name'] = course_info.get('title')
            item['description'] = course_info.get('description')
            item['link'] = f"https://www.edx.org/learn/{course_info.get('slug')}"
            item['provider_url'] = 'https://www.edx.org'
            item['course_creator_urls'] = [school.get('url') for school in course_info.get('schools', [])]
            item['lastmod'] = course_info.get('modifiedDate')
            item['format'] = course_info.get('productType')
            item['has_certificate'] = course_info.get('certificateType') is not None
            item['thumbnail_file'] = course_info.get('cardImageUrl')
            item['content'] = course_info.get('overview')
            item['categories'] = [subject.get('name') for subject in course_info.get('subjects', [])]

            yield item

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")

        self.logger.info(f'Processed course data from {response.url}')


        
