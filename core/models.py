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
    platformCreatorId = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(CreatorType, on_delete=models.SET_NULL, null=True)
    platformThumbnailUrl = models.URLField(max_length=255, blank=True, null=True)
    thumbnailUrl = models.URLField(max_length=255, blank=True, null=True)

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
    isoCode = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    level = models.IntegerField(help_text="1 is the highest level, 2 is sub-category")
    parentTag = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class LearningResource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    platformId = models.ForeignKey(Platform, on_delete=models.CASCADE)
    platformCourseId = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    languages = models.ManyToManyField(Language)
    isFree = models.BooleanField(default=True)
    isLimitedFree = models.BooleanField(default=False)
    dollarPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hasCertificate = models.BooleanField(default=False)
    certificateDollarPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    creators = models.ManyToManyField(Creator)
    formats = models.ManyToManyField(Format)
    tags = models.ManyToManyField(Tag)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    platformLastMod = models.DateTimeField(null=True, blank=True)
    platformThumbnailUrl = models.URLField(max_length=255, blank=True, null=True)
    thumbnailUrl = models.URLField(max_length=255, blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    reviewsCount = models.PositiveIntegerField(default=0)
    reviewsRating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, 
        blank=True
    )
    

    def __str__(self):
        return self.name
