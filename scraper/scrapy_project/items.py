# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LearningResourceItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    provider_url = scrapy.Field()
    course_creator_urls = scrapy.Field()
    lastmod = scrapy.Field()
    format = scrapy.Field()
    has_certificate = scrapy.Field()
    thumbnail_file = scrapy.Field()
    content = scrapy.Field()
    categories = scrapy.Field()
