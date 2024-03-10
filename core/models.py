import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.text import slugify
from django_lifecycle import LifecycleModelMixin, hook, AFTER_CREATE, BEFORE_CREATE
from taggit.managers import TaggableManager


class DigitalLearningResourcePlatform(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    url = models.URLField(blank=True, null=True)
    regex = models.CharField(max_length=200, null=True, blank=True)
    logo = models.ImageField(upload_to='learning-resources/platform-logos', null=True, blank=True)

    def __str__(self):
        return self.name or self.url or f'Digital Resource Platform  {self.pk}'

    class Meta:
        verbose_name = 'Learning Resource Platform'
        verbose_name_plural = 'Learning Resource Platforms'


class DigitalLearningResourceCategory(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True,
                            blank=True, db_index=True)

    def __str__(self):
        return self.name or f'Digital Resource Category {self.pk}'

    class Meta:
        verbose_name = 'Learning Resource Category'
        verbose_name_plural = 'Learning Resource Categories'


class TimestampMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LearningResource(TimestampMixin, models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=200)
    thumbnail_file = models.ImageField(upload_to='learning-resources/thumbnails',
                                       null=True, blank=True)

    active = models.BooleanField(default=True)
    public = models.BooleanField(default=True)

    # created_by = models.ForeignKey('core.User', related_name='created_resources', null=True,
    #                                on_delete=models.SET_NULL)

    extra_data = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder,
                                  help_text="Any additional metadata provided.")

    class Meta:
        abstract = True


class DigitalLearningResource(LifecycleModelMixin, LearningResource):
    external_id = models.CharField(max_length=200, null=True, blank=True,
                                   db_index=True, unique=True)
    thumbnail_url = models.URLField(max_length=450, null=True, blank=True)

    url = models.URLField(max_length=200, null=True, blank=True, unique=True)

    platform = models.ForeignKey('core.DigitalLearningResourcePlatform',
                                 null=True, blank=True,
                                 related_name='digital_learning_resources',
                                 on_delete=models.SET_NULL)

    category = models.ForeignKey('core.DigitalLearningResourceCategory',
                                 null=True, blank=True,
                                 related_name='digital_learning_resources',
                                 on_delete=models.SET_NULL)

    tags = TaggableManager(blank=True, related_name='digital_resources')


    # TODO: Later?
    # file = models.FileField(upload_to='learning-resources/files', null=True, blank=True)

    @classmethod
    def create_unique_slug(cls, name: str):
        base_slug = slugify(name)
        unique_slug = f'{base_slug}-{uuid.uuid4().hex[:8]}'

        while cls.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{base_slug}-{uuid.uuid4().hex[:8]}'
        return unique_slug