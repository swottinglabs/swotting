from django.db.models import Q
from core.models import LearningResource
from typing import Dict, Any
from scrapy.exceptions import DropItem

class DuplicateFilterPipeline:
    """
    Pipeline to filter out duplicate learning resources based on platform_id and platform_course_id.
    """
    
    def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """
        Check if the learning resource already exists in the database.
        """
        if item.get('type') != 'learning_resource':
            return item
            
        data = item.get('data', {})
        platform_id = data.get('platform_id')
        platform_course_id = data.get('platform_course_id')
        
        # Synchronous check
        existing_resource = LearningResource.objects.filter(
            Q(platform_id__name=platform_id) & 
            Q(platform_course_id=platform_course_id)
        ).exists()
        
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
