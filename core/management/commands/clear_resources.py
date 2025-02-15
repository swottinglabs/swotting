import csv
from django.core.management.base import BaseCommand
from core.models import LearningResource
import json


class Command(BaseCommand):
    help = 'Import digital learning resources from a CSV file'

    def handle(self, *args, **options):
        LearningResource.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted all digital learning resources"))
