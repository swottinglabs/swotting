from django.contrib import admin
from .models import (
    Platform,
    Tag,
    LearningResource,
    Level,
    Creator,
    Format,
    Language
)


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_scraping', 'is_independent')
    search_fields = ('name', 'url')
    list_filter = ('is_scraping', 'is_independent')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)


class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform_id', 'url', 'is_free', 'has_certificate')
    search_fields = ('name', 'platform_course_id', 'url')
    list_filter = ('platform_id', 'is_free', 'has_certificate', 'level', 'formats', 'languages')


class CreatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name', 'platform_creator_id')


# Register your models here
admin.site.register(Platform, PlatformAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(LearningResource, LearningResourceAdmin)
admin.site.register(Level)
admin.site.register(Creator, CreatorAdmin)
admin.site.register(Format)
admin.site.register(Language)
