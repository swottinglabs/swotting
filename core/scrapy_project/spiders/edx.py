import json
import os
from scrapy.spiders import SitemapSpider
from scrapy.http import Request
from scrapy.exceptions import CloseSpider

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
                print("data_url: ", data_url)
                yield Request(url=data_url, callback=self.parse_course)

    def parse_course(self, response):
        try:
            # Create a directory to store the response
            os.makedirs('edx_responses', exist_ok=True)

            print("---------------------------------------------------------------------")
            print(response.url)
            print(response)
            
            # Save the response to a file
            filename = f"edx_responses/response_{response.url.split('/')[-2]}.json"
            with open(filename, 'wb') as f:
                f.write(response.body)
            
            self.logger.info(f'Saved response to {filename}')
            
            # Stop the spider after processing the first link
            raise CloseSpider('First link processed')

        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {str(e)}")
