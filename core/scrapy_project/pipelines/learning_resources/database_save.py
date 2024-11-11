from typing import Dict, Any, List
from django.db import transaction
from asgiref.sync import sync_to_async
from core.models import (
    LearningResource,
    Creator,
    Platform,
    Format,
    Language,
    Tag,
    Level
)
from functools import partial

class DatabaseSavePipeline:
    """Pipeline to save validated learning resources and related data to the database"""

    async def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """
        Save the learning resource and its related data to the database.
        
        Args:
            item: Dictionary containing the validated item data
            spider: The spider instance that scraped the item
            
        Returns:
            Dict[str, Any]: The processed item
        """
        if item.get('type') != 'learning_resource':
            return item

        try:
            await self._save_learning_resource(item['data'], spider)
            return item
        except Exception as e:
            spider.logger.error(f'Error saving to database: {str(e)}')
            raise

    async def _get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """Get or create tags by name"""
        tags = []
        for tag_name in tag_names:
            get_or_create_tag = sync_to_async(Tag.objects.get_or_create)
            tag, _ = await get_or_create_tag(name=tag_name.lower().strip())
            tags.append(tag)
        return tags

    async def _save_learning_resource(self, resource_data: Dict[str, Any], spider) -> None:
        """Save learning resource and its related data to the database"""
        
        @sync_to_async
        @transaction.atomic
        def save_to_db():
            # Extract related data
            creators_data = resource_data.pop('creators', [])
            tags_data = resource_data.pop('tags', [])
            language_codes = resource_data.pop('languages', [])
            format_name = resource_data.pop('format', None)
            level_name = resource_data.pop('level', None)
            platform_id = resource_data.pop('platform_id')

            try:
                platform = Platform.objects.get(name=platform_id)
            except Platform.DoesNotExist:
                raise Platform.DoesNotExist(
                    f"Platform '{platform_id}' not found. Please ensure the platform exists in the database."
                )

            # Updated creator handling
            creators = []
            for creator_data in creators_data:
                creator, _ = Creator.objects.update_or_create(
                    platform_id=platform,
                    platform_creator_id=creator_data.get('platform_creator_id'),
                    defaults={
                        'name': creator_data.get('name'),
                        'url': creator_data.get('url'),
                        'platform_thumbnail_url': creator_data.get('platform_thumbnail_url'),
                        'description': creator_data.get('description'),
                    }
                )
                creators.append(creator)

            tags = []
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower().strip())
                tags.append(tag)

            languages = [
                Language.objects.get(iso_code=code)
                for code in language_codes
            ]

            if format_name:
                resource_data['format'] = Format.objects.get(name=format_name)
            if level_name:
                resource_data['level'] = Level.objects.get(name=level_name)

            resource_data['platform_id'] = platform

            # Create or update learning resource
            learning_resource, created = LearningResource.objects.update_or_create(
                platform_id=platform,
                platform_course_id=resource_data['platform_course_id'],
                defaults=resource_data
            )

            # Set many-to-many relationships
            learning_resource.creators.set(creators)
            learning_resource.tags.set(tags)
            learning_resource.languages.set(languages)

            return learning_resource, created

        # Execute the atomic transaction
        learning_resource, created = await save_to_db()

        action = "Created" if created else "Updated"
        spider.logger.info(
            f"{action} learning resource: {learning_resource.name} "
            f"(ID: {learning_resource.id})"
        ) 