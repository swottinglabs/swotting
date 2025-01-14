from django.db import models
import logging
import string
import pandas as pd
from django.db.models import JSONField, IntegerField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.template.defaultfilters import filesizeformat
from scratchy import ScrapedFields as sf, SOFT_REQUIREMENTS
from typing import Tuple, Dict, Any, Optional
import re

logger = logging.getLogger('core.scratchy')


class Spider(models.Model):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'

    LOG_LEVEL_CHOICES = (
        (CRITICAL, 'Critical'),
        (ERROR, 'Error'),
        (WARNING, 'Warning'),
        (INFO, 'Info'),
        (DEBUG, 'Debug'),
        (NOTSET, 'Not Set')
    )

    time_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, blank=True)
    module = models.CharField(max_length=200, unique=True)
    active = models.BooleanField(default=False, db_index=True)
    settings = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder,
                         help_text='Scrapy settings object for this spider only.')
    log_level = models.CharField(max_length=20, default=INFO, choices=LOG_LEVEL_CHOICES)
    faulty = models.BooleanField(default=False, db_index=True)
    crawlera_spider = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f'{self.module}'

    def get_file_name(self):
        return self.module.split('.')[-1]


class Execution(models.Model):
    spider = models.ForeignKey(Spider, on_delete=models.CASCADE)
    stats = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(null=True, blank=True)
    log = models.TextField(blank=True)
    items_scraped = models.IntegerField(null=True)

    @property
    def responses(self):
        return self.stats.get('response_received_count', 0)

    @property
    def finish_reason(self):
        return self.stats.get('finish_reason', '---')

    @property
    def download_size(self):
        b = self.stats.get('downloader/response_bytes', 0)
        return filesizeformat(b)

    @property
    def seconds(self):
        return int(self.stats.get('elapsed_time_seconds', 0))

    def items_as_df(self, stringify_datetime=False) -> pd.DataFrame:
        items = Item.objects.filter(execution=self)

        records = []

        for item in items:
            record = {
                **item.data,
                'time_created': item.time_created if not stringify_datetime else item.time_created.isoformat()
            }
            records.append(record)

        return pd.DataFrame.from_records(records)


class Item(models.Model):
    time_created = models.DateTimeField(auto_now_add=True, db_index=True)
    spider = models.ForeignKey(Spider, on_delete=models.CASCADE, db_index=True)
    execution = models.ForeignKey(Execution, null=True, on_delete=models.SET_NULL)
    data = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    processed = models.BooleanField(default=False, db_index=True)

    @staticmethod
    def _parse_int(s):
        if isinstance(s, str):  # Remove punctuation
            temp = re.findall("(\d+(?:\.\d+)?)", s)
            if len(temp) > 0:
                s = temp[0]
        try:
            val = int(s)
        except (ValueError, TypeError):
            val = None

        return val

    @staticmethod
    def _parse_float(s):
        if isinstance(s, str):  # Remove punctuation
            s = s.replace(',', '')
            temp = re.findall("(\-?\d+(?:\.\d+)?)", s)
            if len(temp) > 0:
                s = temp[0]
        try:
            val = float(s)
        except (ValueError, TypeError):
            val = None
        return val

    @staticmethod
    def _parse_string(s):
        if s is None or isinstance(s, list):
            return None
        try:
            val = str(s)
        except (ValueError, TypeError):
            val = None
        return val
