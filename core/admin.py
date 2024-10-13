from django.contrib import admin
from .models import (
    Platform,
    Tag,
    LearningResource,
    Level,
    CreatorType,
    Creator,
    Format,
    Language
)


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'isScraping', 'isIndependent')
    search_fields = ('name', 'url')
    list_filter = ('isScraping', 'isIndependent')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'parentTag')
    search_fields = ('name',)
    list_filter = ('level',)


class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'platformId', 'url', 'isFree', 'hasCertificate')
    search_fields = ('name', 'platformCourseId', 'url')
    list_filter = ('platformId', 'isFree', 'hasCertificate', 'level', 'formats', 'languages')


class CreatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'type')
    search_fields = ('name', 'platformCreatorId')
    list_filter = ('type',)


# Register your models here
admin.site.register(Platform, PlatformAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(LearningResource, LearningResourceAdmin)
admin.site.register(Level)
admin.site.register(CreatorType)
admin.site.register(Creator, CreatorAdmin)
admin.site.register(Format)
admin.site.register(Language)
