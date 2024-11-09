# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from core.models import LearningResource, Creator


class ScrapyProjectPipeline:
    def process_item(self, item, spider):
        return item

class CreatorPipeline:
    def process_item(self, item, spider):
        # for creator in item['creators']:
        #     Creator.objects.create(**creator)
        return item


class LearningResourcePipeline:
    def process_item(self, item, spider):
        # Transform and save the item
        # LearningResource.objects.create(**item)
        return item