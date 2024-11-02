import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Level(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CreatorType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Creator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255, blank=True, null=True)
    platform_creator_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(CreatorType, on_delete=models.SET_NULL, null=True)
    platform_thumbnail_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Platform(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    isScraping = models.BooleanField(default=False)
    lastFullScrape = models.DateTimeField(null=True, blank=True)
    isIndependent = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Format(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Language(models.Model):
    iso_code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class LearningResource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scraped_timestamp = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    platform_id = models.ForeignKey(Platform, on_delete=models.CASCADE)
    platform_course_id = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)
    short_description = models.TextField()
    description = models.TextField()
    html_description = models.TextField(blank=True, null=True)
    languages = models.ManyToManyField(Language)
    is_free = models.BooleanField(default=True)
    is_limited_free = models.BooleanField(default=False)
    dollar_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    has_certificate = models.BooleanField(default=False)
    creators = models.ManyToManyField(Creator)
    formats = models.ManyToManyField(Format)
    tags = models.ManyToManyField(Tag)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    platform_last_update = models.DateTimeField(null=True, blank=True)
    platform_thumbnail_url = models.URLField(max_length=255, blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    platform_reviews_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    enrollment_count = models.PositiveIntegerField(default=0)
    platform_reviews_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, 
        blank=True
    )
    

    def __str__(self):
        return self.name
