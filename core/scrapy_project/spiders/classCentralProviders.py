from pathlib import Path
import scrapy

class ProvidersSpider(scrapy.Spider):
    name = "classCentralProviders"
    start_urls = [
        "https://www.classcentral.com/providers",
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    }

    def parse(self, response):
        # Delegate the processing of providers to the get_providers function
        return self.get_providers(response)


    def get_providers(self, response):

        providers = []

        # Loop through each provider in the list
        for provider in response.xpath('//li[contains(@class, "width-100 border-bottom border-box")]'):
            # Extract the name and URL of each provider
            name = provider.xpath('.//span[contains(@class, "text-1 line-tight color-charcoal weight-semi block")]/text()').get()
            relative_url = provider.xpath('./a/@href').get()
            url = response.urljoin(relative_url)  # Convert relative URL to absolute URL

            # Create a dictionary with the provider name and URL
            item = {
                'name': name,
                'url': url,
            }

            providers.append(item)
            
        self.getAllLinksFromProviders(providers)


    def getAllLinksFromProviders (self, providers):
        
        



        print(providers)  # For demonstration, just print the item
