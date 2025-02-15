from django.db.models import Q
from core.models import LearningResource
from typing import Dict, Any
from scrapy.exceptions import DropItem
from asgiref.sync import sync_to_async

class DuplicateFilterPipeline:
    """
    Pipeline to filter out duplicate learning resources based on platform_id and platform_course_id.
    """
    
    async def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """
        Check if the learning resource already exists in the database.
        """
        if item.get('type') != 'learning_resource':
            return item
            
        data = item.get('data', {})
        platform_id = data.get('platform_id')
        platform_course_id = data.get('platform_course_id')
        
        # Wrap the synchronous check in sync_to_async
        existing_resource = await sync_to_async(self._check_duplicate)(platform_id, platform_course_id)
        
        if existing_resource:
            spider.logger.info(
                f'Dropping duplicate item - Platform: {platform_id}, '
                f'Course ID: {platform_course_id}'
            )
            raise DropItem(
                f'Duplicate item found for platform {platform_id} '
                f'and course ID {platform_course_id}'
            )
        
        return item

    def _check_duplicate(self, platform_id: str, platform_course_id: str) -> bool:
        """
        Synchronous method to check for duplicates in the database.
        """
        return LearningResource.objects.filter(
            Q(platform_id__name=platform_id) & 
            Q(platform_course_id=platform_course_id)
        ).exists()
