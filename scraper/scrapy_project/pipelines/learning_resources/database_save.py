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
import datetime

# Set up direct debug printing
def db_print(message, level="INFO"):
    """Print database debug info to console"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"DB {level} [{timestamp}]: {message}")

# Log initialization
db_print(f"Database pipeline initialized")
db_print(f"Current working directory: {os.getcwd()}")

logger = logging.getLogger(__name__)

class DatabaseSavePipeline:
    """Pipeline to save validated learning resources and related data to the database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Add debug information about database configuration
        db_url = os.environ.get('DATABASE_URL', 'Not set in environment')
        self.logger.info(f"DatabaseSavePipeline initialized with DATABASE_URL environment: {db_url}")
        db_print(f"DatabaseSavePipeline initialized with DATABASE_URL environment: {db_url}")
        
        # Print current database connection info
        db_settings = connections.databases.get('default')
        if db_settings:
            # Remove sensitive info before logging
            db_host = db_settings.get('HOST', 'unknown')
            db_port = db_settings.get('PORT', 'unknown')
            db_name = db_settings.get('NAME', 'unknown')
            msg = f"Current database connection settings: HOST={db_host}, PORT={db_port}, NAME={db_name}"
            self.logger.info(msg)
            db_print(msg)
        else:
            msg = "Could not retrieve database connection settings"
            self.logger.warning(msg)
            db_print(msg, "WARNING")

        # Try to verify write access
        try:
            test_file = "db_test.txt"
            with open(test_file, 'w') as f:
                f.write("Test")
            os.remove(test_file)
            db_print("Successfully tested file write permission")
        except Exception as e:
            db_print(f"No write permission in current directory: {e}", "WARNING")

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
            db_print(f"Skipping non-learning-resource item type: {item.get('type')}")
            return item

        try:
            resource_name = item['data'].get('name', 'unnamed')
            db_print(f"Processing learning resource: {resource_name}")
            self.logger.info(f"Processing learning resource: {resource_name}")
            
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

            # Save to database
            db_print(f"Calling _save_learning_resource for: {resource_name}")
            self._save_learning_resource(data, spider)
            db_print(f"Successfully saved learning resource: {resource_name}")
            self.logger.info(f"Successfully saved learning resource: {resource_name}")
            return item
        except Exception as e:
            spider.logger.error(f'Error saving to database: {str(e)}')
            db_print(f'Error saving to database: {str(e)}', "ERROR")
            # More detailed error information
            import traceback
            trace = traceback.format_exc()
            self.logger.error(f"Full error traceback: {trace}")
            db_print(f"Full error traceback: {trace}", "ERROR")
            raise

    def _get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """Get or create tags by name using the Tag model's helper method"""
        return Tag.get_or_create_tags(tag_names)

    def _save_learning_resource(self, data: Dict[str, Any], spider) -> None:
        """Synchronous method to save learning resource to database"""
        try:
            resource_name = data.get('name', 'unnamed')
            db_print(f"Starting database transaction for learning resource: {resource_name}")
            self.logger.info(f"Starting database transaction for learning resource: {resource_name}")
            
            with transaction.atomic():
                # Get or create platform
                db_print("Creating or getting platform")
                platform, platform_created = Platform.objects.get_or_create(
                    name=data['platform_id']
                )
                db_print(f"Platform: {platform.name} ({'created' if platform_created else 'existing'})")
                self.logger.info(f"Platform: {platform.name} ({'created' if platform_created else 'existing'})")

                # Get or create format
                format_name = data.get('format')
                format_obj = None
                if format_name:
                    db_print(f"Creating or getting format: {format_name}")
                    format_obj, format_created = Format.objects.get_or_create(
                        name=format_name
                    )
                    db_print(f"Format: {format_obj.name} ({'created' if format_created else 'existing'})")
                    self.logger.info(f"Format: {format_obj.name} ({'created' if format_created else 'existing'})")

                # Get or create level
                level_name = data.get('level')
                level_obj = None
                if level_name:
                    db_print(f"Creating or getting level: {level_name}")
                    level_obj, level_created = Level.objects.get_or_create(
                        name=level_name
                    )
                    db_print(f"Level: {level_obj.name} ({'created' if level_created else 'existing'})")
                    self.logger.info(f"Level: {level_obj.name} ({'created' if level_created else 'existing'})")

                # Create or update creators
                creators = []
                db_print(f"Processing {len(data.get('creators', []))} creators")
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
                    db_print(f"Creator: {creator.name} ({'created' if creator_created else 'existing'})")
                    self.logger.info(f"Creator: {creator.name} ({'created' if creator_created else 'existing'})")

                # Get or create languages
                languages = []
                db_print(f"Processing {len(data.get('languages', []))} languages")
                for lang_code in data.get('languages', []):
                    lang, lang_created = Language.objects.get_or_create(
                        iso_code=lang_code,
                        defaults={'name': lang_code}
                    )
                    languages.append(lang)
                    db_print(f"Language: {lang.iso_code} ({'created' if lang_created else 'existing'})")
                    self.logger.info(f"Language: {lang.iso_code} ({'created' if lang_created else 'existing'})")

                # Get or create tags
                db_print(f"Processing {len(data.get('tags', []))} tags")
                tags = Tag.get_or_create_tags(data.get('tags', []))
                db_print(f"Created/found {len(tags)} tags")
                self.logger.info(f"Created/found {len(tags)} tags")

                # Create or update learning resource
                db_print("About to create or update learning resource")
                
                # Print key fields for debugging
                db_print(f"Platform ID: {platform.id}, Platform course ID: {data['platform_course_id']}")
                
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
                
                db_print(f"Resource {'created' if created else 'updated'} with ID: {resource.id}")

                # Set many-to-many relationships
                db_print("Setting many-to-many relationships")
                resource.creators.set(creators)
                resource.languages.set(languages)
                resource.tags.set(tags)

                # Log success
                action = "Created" if created else "Updated"
                msg = f"{action} learning resource: {data['name']} (Platform: {platform.name}, ID: {data['platform_course_id']})"
                self.logger.info(msg)
                db_print(msg)
                
                # Try to verify that the resource was actually saved
                verification = LearningResource.objects.filter(
                    platform_id=platform,
                    platform_course_id=data['platform_course_id']
                ).exists()
                
                msg = f"Verification of save - resource exists in DB: {verification}"
                self.logger.info(msg)
                db_print(msg)
                
                # Check row count as a sanity check
                count = LearningResource.objects.count()
                db_print(f"Total learning resources in database: {count}")

        except Exception as e:
            self.logger.error(f"Error saving learning resource {data.get('name')}: {str(e)}")
            db_print(f"Error saving learning resource {data.get('name')}: {str(e)}", "ERROR")
            import traceback
            trace = traceback.format_exc()
            self.logger.error(f"Full error traceback: {trace}")
            db_print(f"Full error traceback: {trace}", "ERROR")
            raise 