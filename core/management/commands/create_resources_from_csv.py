import csv
from django.core.management.base import BaseCommand
from core.models import DigitalLearningResource, DigitalLearningResourcePlatform, DigitalLearningResourceCategory
from core.utils import determine_platform_name_from_slug_code


class Command(BaseCommand):
    help = 'Import digital learning resources from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        # Initialize a list to store DigitalLearningResource instances
        digital_learning_resources = []

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Load the data from the CSV file
                provider_slug = row.get('provider_slug', None)
                resource_name = row.get('course_name', None)
                resource_url = row.get('url_classCentral', None)
                resource_external_id = row.get('end_url', resource_url)
                resource_language = row.get('language', None)
                resource_summary = row.get('summary', None)
                resource_duration = row.get('duration', None)
                resource_entity_url = row.get('entity_url', None)
                resource_source = row.get('source', None)
                resource_type = row.get('type', None)

                # Digital resource properties
                """
                    name
                    slug
                    thumbnail_file
                    active
                    public
                    external_id
                    thumbnail_url
                    url
                    platform
                    category
                    tags
                    extra_data
                """
                default_resource_category, _ = DigitalLearningResourceCategory.objects.get_or_create(
                    name='Online Course'
                )
                platform_name = determine_platform_name_from_slug_code(provider_slug)
                platform, _ = DigitalLearningResourcePlatform.objects.get_or_create(
                    name=platform_name
                )
                unique_slug = DigitalLearningResource.create_unique_slug(resource_name)

                # Instead of creating each instance individually, append it to the list
                digital_learning_resources.append(DigitalLearningResource(
                    name=resource_name,
                    slug=unique_slug,
                    active=True,
                    public=True,
                    external_id=resource_external_id or resource_url,
                    thumbnail_url=None,
                    url=resource_url,
                    platform=platform,
                    category=default_resource_category,
                    # tags=None,  # Note: We'lll need to handle tags separately as bulk_create doesn't support many-to-many relationships
                    extra_data={
                        'language': resource_language or '',
                        'summary': resource_summary or '',
                        'duration': resource_duration or '',
                        'entity_url': resource_entity_url or '',
                        'source': resource_source or '',
                        'type': resource_type or ''
                    }
                ))

        # Use bulk_create to insert all instances at once
        DigitalLearningResource.objects.bulk_create(digital_learning_resources)


        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported {len(digital_learning_resources)} digital learning resources"))
