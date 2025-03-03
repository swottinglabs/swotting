from typing import Dict, Any, List
from django.db import transaction, connections
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
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseSavePipeline:
    """Pipeline to save validated learning resources and related data to the database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Add debug information about database configuration
        db_url = os.environ.get('DATABASE_URL', 'Not set in environment')
        self.logger.info(f"DatabaseSavePipeline initialized with DATABASE_URL environment: {db_url}")
        
        # Print current database connection info
        db_settings = connections.databases.get('default')
        if db_settings:
            # Remove sensitive info before logging
            safe_db_settings = {k: v for k, v in db_settings.items() 
                               if k not in ('PASSWORD', 'USER', 'NAME')}
            self.logger.info(f"Current database connection settings: HOST={db_settings.get('HOST', 'unknown')}, PORT={db_settings.get('PORT', 'unknown')}")
        else:
            self.logger.warning("Could not retrieve database connection settings")

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

    def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """
        Save the learning resource and its related data to the database.
        """
        if item.get('type') != 'learning_resource':
            self.logger.info(f"Skipping non-learning-resource item type: {item.get('type')}")
            return item

        try:
            self.logger.info(f"Processing learning resource: {item['data'].get('name', 'unnamed')}")
            
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

            self._save_learning_resource(data, spider)
            self.logger.info(f"Successfully saved learning resource: {data.get('name')}")
            return item
        except Exception as e:
            spider.logger.error(f'Error saving to database: {str(e)}')
            # More detailed error information
            import traceback
            self.logger.error(f"Full error traceback: {traceback.format_exc()}")
            raise

    def _get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """Get or create tags by name using the Tag model's helper method"""
        return Tag.get_or_create_tags(tag_names)

    def _save_learning_resource(self, data: Dict[str, Any], spider) -> None:
        """Synchronous method to save learning resource to database"""
        try:
            self.logger.info(f"Starting database transaction for learning resource: {data.get('name')}")
            
            with transaction.atomic():
                # Get or create platform
                platform, platform_created = Platform.objects.get_or_create(
                    name=data['platform_id']
                )
                self.logger.info(f"Platform: {platform.name} ({'created' if platform_created else 'existing'})")

                # Get or create format
                format_name = data.get('format')
                format_obj = None
                if format_name:
                    format_obj, format_created = Format.objects.get_or_create(
                        name=format_name
                    )
                    self.logger.info(f"Format: {format_obj.name} ({'created' if format_created else 'existing'})")

                # Get or create level
                level_name = data.get('level')
                level_obj = None
                if level_name:
                    level_obj, level_created = Level.objects.get_or_create(
                        name=level_name
                    )
                    self.logger.info(f"Level: {level_obj.name} ({'created' if level_created else 'existing'})")

                # Create or update creators
                creators = []
                for creator_data in data.get('creators', []):
                    creator, creator_created = Creator.objects.get_or_create(
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
                    self.logger.info(f"Creator: {creator.name} ({'created' if creator_created else 'existing'})")

                # Get or create languages
                languages = []
                for lang_code in data.get('languages', []):
                    lang, lang_created = Language.objects.get_or_create(
                        iso_code=lang_code,
                        defaults={'name': lang_code}
                    )
                    languages.append(lang)
                    self.logger.info(f"Language: {lang.iso_code} ({'created' if lang_created else 'existing'})")

                # Get or create tags
                tags = Tag.get_or_create_tags(data.get('tags', []))
                self.logger.info(f"Created/found {len(tags)} tags")

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
                
                # Try to verify that the resource was actually saved
                verification = LearningResource.objects.filter(
                    platform_id=platform,
                    platform_course_id=data['platform_course_id']
                ).exists()
                self.logger.info(f"Verification of save - resource exists in DB: {verification}")

        except Exception as e:
            self.logger.error(f"Error saving learning resource {data.get('name')}: {str(e)}")
            import traceback
            self.logger.error(f"Full error traceback: {traceback.format_exc()}")
            raise 