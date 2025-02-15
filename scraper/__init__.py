from scrapy.utils.reactor import install_reactor

# Install asyncio reactor before any other imports
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
