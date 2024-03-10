import csv
from django.core.management.base import BaseCommand
from core.models import DigitalLearningResource, DigitalLearningResourcePlatform, DigitalLearningResourceCategory

class Command(BaseCommand):
    help = 'Import digital learning resources from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                print('\n\n')
                provider_slug = row.get('provider_slug', None)
                resource_name = row.get('course_name', None)
                resource_url = row.get('url_classCentral', None)
                resource_external_id = row.get('end_url', None)
                resource_language = row.get('language', None)
                resource_summary = row.get('summary', None)
                resource_duration = row.get('duration', None)
                resource_entity_url = row.get('entity_url', None)
                resource_source = row.get('source', None)
                resource_type = row.get('type', None)


        self.stdout.write(self.style.SUCCESS(f"Successfully imported {row['course_name']}"))
