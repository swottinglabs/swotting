import csv
import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from core.models import Level, Creator, Platform, Format, Language, Tag, LearningResource

class Command(BaseCommand):
    help = 'Initialize database with initial data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_dir = 'core/init_data'
        # List of models to handle
        self.models = [Level, Creator, Platform, Format, Language, Tag, LearningResource]

    def get_user_confirmation(self):
        """Helper function to get user confirmation for data deletion"""
        while True:
            # response = input('Do you want to delete all existing data before initialization? (y/n): ').lower()
            response = 'y'
            if response in ['y', 'n']:
                return response == 'y'
            self.stdout.write(self.style.WARNING('Please enter y or n'))

    def delete_all_data(self):
        """Helper function to delete all data from models"""
        for model in reversed(self.models):  # Reverse to handle foreign key dependencies
            self.stdout.write(f'Deleting all {model.__name__} records...')
            model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'All {model.__name__} records deleted'))
    
    


    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database initialization process...')
        
        # Prompt for data deletion
        if self.get_user_confirmation():
            self.delete_all_data()        
        

        self.stdout.write('Initializing database with new data...')

        # Initialize models
        for model in self.models:
            filename = f"{model.__name__.lower()}.csv"
            self.init_model(model, filename)

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
 