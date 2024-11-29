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

    @classmethod
    def scraped_field_names(self):
        return sf()

    def parse_scraped_field(self, fieldname: str):
        if fieldname == sf.url:
            return self.data.get(sf.url, None)
        if fieldname == sf.title:
            return self._parse_string(self.data.get(fieldname, None))
        if fieldname == sf.description:
            return self._parse_string(self.data.get(fieldname, None))
        if fieldname == sf.area:
            return self._parse_area()
        if fieldname == sf.agency:
            return self.data.get(fieldname, None)
        if fieldname == sf.offering:
            return self.data.get(sf.offering, None)
        elif fieldname == sf.property_type:
            return self.data.get(sf.property_type, None)
        elif fieldname == sf.price:
            return self._parse_price(self.data.get(sf.price, ''))
        elif fieldname == sf.images:
            return self._parse_images()
        elif fieldname == sf.bedrooms:
            return self._parse_bedrooms()
        elif fieldname == sf.bathrooms:
            return self._parse_bathrooms()
        elif fieldname == sf.garages:
            return self._parse_garages()
        elif fieldname == sf.parkings:
            return self._parse_parkings()
        elif fieldname == sf.latitude:
            return self._parse_latitude()
        elif fieldname == sf.longitude:
            return self._parse_longitude()
        elif fieldname == sf.erf_size:
            return self._parse_erf_size()
        elif fieldname == sf.floor_size:
            return self._parse_floor_size()
        elif fieldname == sf.banner:
            return self._parse_banner()
        elif fieldname == sf.sold_tag:
            return self._parse_sold_tag()
        elif fieldname == sf.contact_name:
            return self._parse_contact_name()
        elif fieldname == sf.contact_email:
            return self._parse_contact_email()
        elif fieldname == sf.contact_num:
            return self._parse_contact_number()
        elif fieldname == sf.listing_date:
            return self._parse_listing_date()
        elif fieldname == sf.rent_duration:
            return self._parse_rent_duration()
        elif fieldname == sf.price_per_m2:
            return self._parse_price(self.data.get(sf.price_per_m2))
        elif fieldname == sf.street_address:
            return self._parse_street_address()
        elif fieldname == sf.hybrid_listed_by:
            return self._parse_hybrid_listed_by()
        elif fieldname == sf.hybrid_listing_body:
            return self._parse_hybrid_listing_body()
        else:
            return None

    def get_hard_reqs(self) -> Tuple:
        """Gets the external id and agency of an item

        Returns:
           tuple containing external_id and agency of the item
        """
        from core.models import Agency
        external_id = self.data.get("external_id")
        url = self.data.get("url")
        spider = self.spider
        try:
            agency = Agency.objects.get(spider=spider)
        except Agency.DoesNotExist:
            agency = None
        return external_id, url, agency

    def validate_hard_requirements(self, unknown_agency) -> bool:
        """Validate the required arguments of each item.

        The items with invalid requirements will be stored.

        Args:
            unknown_agency: the unknown agency helper

        Excepts:
            Agency.DoesNotExist

        Returns:
            bool indicating if hard requirements are valid
        """
        from core.models import Agency
        valid = True

        # Check if item has all requirements
        external_id, url, agency = self.get_hard_reqs()
        invalid = not external_id or not url

        # Check the agency
        agency = Agency.validate_agency_exists(self)
        invalid_agency = not agency or agency == unknown_agency

        if invalid or invalid_agency:
            # TODO: Logging @Gerrie
            # self._invalid_items.append(item.id)
            # if item.spider is not None:
            #     if item.spider.name not in self._invalid_spiders:
            #         self._invalid_spiders.append(item.spider.name)
            return False
        return True

    def validate_soft_requirements(self) -> list:
        """Validate the soft requirements of each item.

        This function will only log the missing requirements, nothing more.

        Returns:
            None
        """
        missing_requirements = []
        for field_name in SOFT_REQUIREMENTS:
            if self.data.get(field_name, None) is None:
                missing_requirements.append(field_name)
        return missing_requirements


    def _validate_agency_exists(self):
        """This function will check if agency exists.

        # FIXME: @Peter maybe we could move this function to agency model

        The function will check if the agency for a given spider is created.
        The non-existing agencies will be logged and added to metadata.

        Returns:
            Agency
        """
        from core.models import Agency
        if self.spider is None:
            raise Exception(f'No spider for Item (id={self.id})')
        try:
            agency = Agency.objects.get(spider=self.spider)
        except Agency.DoesNotExist:
            agency = None
        return agency

    def _parse_price(self, s) -> Optional[int]:
        """Parse the price field to get an integer or None value."""
        if s is None:
            return s
        if not isinstance(s, str):
            s = str(s)
        try:
            price = self._parse_float(s)
        except:
            logger.error(f'Error parsing price {s}')
            try:
                price = (s
                         .strip()
                         .lstrip('R')
                         .replace(',', ''))
            except Exception as e:
                logger.error(f'Error parsing price {s}, e={str(e)}')
                price = None
                return price
        try:
            price = int(price)
        except (ValueError, TypeError):
            price = None
        if isinstance(price, int):
            if price > 1000000000:  # Price too large for db to handle
                price = 1000000000
                msg = f'item {self.id} is storing a price that is too large.'
                logger.warning(msg)
        return price

    def _parse_area(self) -> str:
        """Parse the area field to get the correct area"""
        scraped_area = self.data.get('area', '')
        if not isinstance(scraped_area, str):
            scraped_area = ''
        scraped_area = scraped_area.lower()
        # Remove punctuation
        scraped_area = scraped_area.translate(str.maketrans('', '', string.punctuation))
        # Remove numbers
        scraped_area = ''.join([i for i in scraped_area if not i.isdigit()]).strip()
        # Remove stop words
        stop_words = ['street', 'road', 'apartment', 'rd', 'str', 'boulevard', 'blvd']
        scraped_area = [word for word in scraped_area.split(' ') if word not in stop_words]
        scraped_area = ' '.join(scraped_area)
        # remove references to 'Cape Town', 'Western Cape' and 'South Africa' so as to improve place matching
        scraped_area = scraped_area.replace('cape town', '').strip()
        scraped_area = scraped_area.replace('western cape', '').strip()
        scraped_area = scraped_area.replace('south africa', '').strip()
        return scraped_area

    def _parse_offering(self):
        return self._parse_string(self.data.get('offering', None))

    def _property_type(self):
        return self._parse_string(self.data.get('property_type', None))

    def _parse_garages(self):
        return self._parse_int(self.data.get(sf.garages))

    def _parse_parkings(self):
        return self._parse_int(self.data.get(sf.parkings))

    def _parse_bedrooms(self):
        return self._parse_float(self.data.get(sf.bedrooms))

    def _parse_bathrooms(self):
        return self._parse_float(self.data.get(sf.bathrooms))

    def _parse_images(self):
        images = self.data.get(sf.images, [])
        if not isinstance(images, list):
            return []
        return images

    def _parse_latitude(self):
        return self._parse_float(self.data.get(sf.latitude))

    def _parse_longitude(self):
        return self._parse_float(self.data.get(sf.longitude))

    def _parse_erf_size(self):
        return self._parse_float(self.data.get(sf.erf_size))

    def _parse_floor_size(self):
        return self._parse_float(self.data.get(sf.floor_size))

    def _parse_levy(self):
        return self._parse_int(self.data.get(sf.levy, None))

    def _parse_rent_duration(self):
        rental_type = self.data.get(sf.rent_duration, None)
        if isinstance(rental_type, list):
            if len(rental_type) > 0:
                rental_type = rental_type[0]
            else:
                rental_type = None
        if isinstance(rental_type, str):
            rental_type = rental_type.lower().strip()
        return self._parse_string(rental_type)

    def _parse_rates(self):
        return self._parse_int(self.data.get(sf.rates, None))

    def _parse_banner(self) -> list:
        banner = self.data.get(sf.banner, None)
        if isinstance(banner, list):
            banner = [self._parse_string(s).replace('\n', '').strip().lower() \
                      for s in banner if s is not None]
        elif isinstance(banner, str):
            banner = [self._parse_string(banner).replace('\n', '').strip().lower()]
        return banner

    def _parse_sold_tag(self):
        return self._parse_string(self.data.get(sf.sold_tag, None))

    def _parse_contact_name(self):
        return self._parse_string(self.data.get(sf.contact_name, None))

    def _parse_contact_number(self):
        return self._parse_string(self.data.get(sf.contact_num, None))

    def _parse_contact_email(self):
        return self._parse_string(self.data.get(sf.contact_email, None))

    def _parse_listing_date(self):
        return self._parse_string(self.data.get(sf.listing_date, None))

    def _parse_street_address(self):
        return self._parse_string(self.data.get(sf.street_address, None))

    def _parse_hybrid_listed_by(self) -> str:
        hybrid_listed_by = self.data.get(sf.hybrid_listed_by, None)
        if isinstance(hybrid_listed_by, list):
            if len(hybrid_listed_by) > 0:
                hybrid_listed_by = hybrid_listed_by[0]
            else:
                hybrid_listed_by = None
        if isinstance(hybrid_listed_by, str):
            hybrid_listed_by = hybrid_listed_by.lower().strip()
        return self._parse_string(hybrid_listed_by)

    def _parse_hybrid_listing_body(self):
        listing_body = self.data.get(sf.hybrid_listing_body, None)
        if isinstance(listing_body, list):
            if len(listing_body) > 0:
                listing_body = listing_body[0]
            else:
                listing_body = None
        if isinstance(listing_body, str):
            listing_body = listing_body.lower().strip()
        return self._parse_string(listing_body)

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
