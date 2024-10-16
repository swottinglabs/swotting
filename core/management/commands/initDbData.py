import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Level, CreatorType, Creator, Platform, Format, Language, Tag, LearningResource

class Command(BaseCommand):
    help = 'Initialize database with initial data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_dir = 'core/init_data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing database...')

        self.init_model(Level, 'levels.csv')
        self.init_model(CreatorType, 'creator_types.csv')
        self.init_model(Creator, 'creators.csv')
        self.init_model(Platform, 'platforms.csv')
        self.init_model(Format, 'formats.csv')
        self.init_model(Language, 'languages.csv')
        self.init_model(Tag, 'tags.csv')
        self.init_model(LearningResource, 'learning_resources.csv')

        self.stdout.write(self.style.SUCCESS('Database initialization complete'))

    def init_model(self, model, filename):
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            self.stdout.write(f'Initializing {model.__name__}...')
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.create_instance(model, row)
            self.stdout.write(self.style.SUCCESS(f'{model.__name__} initialized'))
        else:
            self.stdout.write(f'No data file found for {model.__name__}, skipping...')

    def create_instance(self, model, data):
        if model == Tag:
            # Special handling for Tag model due to self-referential relationship
            parent_tag_name = data.get('parent_tag')
            if parent_tag_name:
                parent_tag, _ = Tag.objects.get_or_create(name=parent_tag_name)
                data['parentTag'] = parent_tag
            else:
                data['parentTag'] = None

        # Remove any keys from data that are not fields in the model
        model_fields = [f.name for f in model._meta.get_fields()]
        filtered_data = {k: v for k, v in data.items() if k in model_fields and v != ''}

        # Create the instance
        instance, created = model.objects.get_or_create(**filtered_data)
        if created:
            self.stdout.write(f'Created {model.__name__}: {instance}')
 