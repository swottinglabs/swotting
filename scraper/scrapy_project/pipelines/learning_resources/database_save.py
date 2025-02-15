from typing import Dict, Any, List
from django.db import transaction
from core.models import (
    LearningResource,
    Creator,
    Platform,
    Format,
    Language,
    Tag,
    Level
)
from urllib.parse import urlparse
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class DatabaseSavePipeline:
    """Pipeline to save validated learning resources and related data to the database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _clean_url(self, url: Any) -> str:
        """Clean and validate URL"""
        if not url:
            return None
        if hasattr(url, '__str__'):
            url = str(url)
        try:
            parsed = urlparse(url)
            return url if parsed.scheme and parsed.netloc else None
        except Exception:
            return None

    async def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """
        Save the learning resource and its related data to the database.
        """
        if item.get('type') != 'learning_resource':
            return item

        try:
            # Clean URLs before saving
            data = item['data']
            if 'url' in data:
                data['url'] = self._clean_url(data['url'])
            if 'thumbnail_url' in data:
                data['thumbnail_url'] = self._clean_url(data['thumbnail_url'])
                
            # Clean creator URLs
            if 'creators' in data:
                for creator in data['creators']:
                    if 'url' in creator:
                        creator['url'] = self._clean_url(creator['url'])
                    if 'platform_thumbnail_url' in creator:
                        creator['platform_thumbnail_url'] = self._clean_url(creator['platform_thumbnail_url'])

            await sync_to_async(self._save_learning_resource)(data, spider)
            return item
        except Exception as e:
            spider.logger.error(f'Error saving to database: {str(e)}')
            raise

    def _get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """Get or create tags by name using the Tag model's helper method"""
        return Tag.get_or_create_tags(tag_names)

    def _save_learning_resource(self, data: Dict[str, Any], spider) -> None:
        """Synchronous method to save learning resource to database"""
        try:
            with transaction.atomic():
                # Get or create platform
                platform, _ = Platform.objects.get_or_create(
                    name=data['platform_id']
                )

                # Get or create format
                format_name = data.get('format')
                format_obj = None
                if format_name:
                    format_obj, _ = Format.objects.get_or_create(
                        name=format_name
                    )

                # Get or create level
                level_name = data.get('level')
                level_obj = None
                if level_name:
                    level_obj, _ = Level.objects.get_or_create(
                        name=level_name
                    )

                # Create or update creators
                creators = []
                for creator_data in data.get('creators', []):
                    creator, _ = Creator.objects.get_or_create(
                        platform_id=platform,
                        platform_creator_id=creator_data['platform_creator_id'],
                        defaults={
                            'name': creator_data['name'],
                            'url': creator_data.get('url'),
                            'description': creator_data.get('description', ''),
                            'platform_thumbnail_url': creator_data.get('platform_thumbnail_url')
                        }
                    )
                    creators.append(creator)

                # Get or create languages
                languages = []
                for lang_code in data.get('languages', []):
                    lang, _ = Language.objects.get_or_create(
                        iso_code=lang_code,
                        defaults={'name': lang_code}  # Simple default, you might want to map proper names
                    )
                    languages.append(lang)

                # Get or create tags
                tags = Tag.get_or_create_tags(data.get('tags', []))

                # Create or update learning resource
                resource, created = LearningResource.objects.get_or_create(
                    platform_id=platform,
                    platform_course_id=data['platform_course_id'],
                    defaults={
                        'name': data['name'],
                        'description': data['description'],
                        'short_description': data.get('short_description', ''),
                        'url': data['url'],
                        'platform_thumbnail_url': data.get('platform_thumbnail_url'),
                        'is_free': data.get('is_free', False),
                        'is_limited_free': data.get('is_limited_free', False),
                        'dollar_price': data.get('dollar_price'),
                        'has_certificate': data.get('has_certificate', False),
                        'level': level_obj,
                        'format': format_obj,
                        'duration_h': data.get('duration_h'),
                        'platform_reviews_count': data.get('platform_reviews_count'),
                        'platform_reviews_rating': data.get('platform_reviews_rating'),
                        'enrollment_count': data.get('enrollment_count'),
                        'is_active': data.get('is_active', True),
                        'html_description': data.get('html_description'),
                        'platform_last_update': data.get('platform_last_update'),
                    }
                )

                # Set many-to-many relationships
                resource.creators.set(creators)
                resource.languages.set(languages)
                resource.tags.set(tags)

                # Log success
                action = "Created" if created else "Updated"
                self.logger.info(
                    f"{action} learning resource: {data['name']} "
                    f"(Platform: {platform.name}, ID: {data['platform_course_id']})"
                )

        except Exception as e:
            self.logger.error(f"Error saving learning resource {data.get('name')}: {str(e)}")
            raise 