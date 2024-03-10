import csv
from django.core.management.base import BaseCommand
from core.models import DigitalLearningResource, DigitalLearningResourcePlatform, DigitalLearningResourceCategory

class Command(BaseCommand):
    help = 'Import digital learning resources from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        platform_slugs = {}

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                provider_slug = row['provider_slug']
                example_url = row['end_url']
                if provider_slug not in platform_slugs:
                    platform_slugs[provider_slug] = {
                        'name': provider_slug,
                    }
                elif example_url and not platform_slugs[provider_slug].get('example_url'):
                    platform_slugs['example_url'] = example_url

        for k, v in platform_slugs.items():
            name = v.get('name', None)
            if name is not None:
                platform_name = name.capitalize().replace('-', ' ').replace('_', ' ')
                existing_platform = DigitalLearningResourcePlatform.objects.filter(name=platform_name).first()
                if existing_platform is None:
                    DigitalLearningResourcePlatform.objects.create(name=platform_name)
        self.stdout.write(self.style.SUCCESS(f"Created categories"))
