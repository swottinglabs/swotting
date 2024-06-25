from django.contrib import admin
from .models import (
    DigitalLearningResourcePlatform,
    DigitalLearningResourceCategory,
    LearningResource,
    DigitalLearningResource,
    WaitlistEntry
)


class DigitalLearningResourcePlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name', 'url')


class DigitalLearningResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class DigitalLearningResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'platform', 'category', 'external_id', 'url')
    search_fields = ('name', 'slug', 'external_id', 'url')
    list_filter = ('platform', 'category')


class WaitingListEntryAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    list_filter = ('created_at',)


admin.site.register(DigitalLearningResourcePlatform, DigitalLearningResourcePlatformAdmin)
admin.site.register(DigitalLearningResourceCategory, DigitalLearningResourceCategoryAdmin)
admin.site.register(DigitalLearningResource, DigitalLearningResourceAdmin)
admin.site.register(WaitlistEntry, WaitingListEntryAdmin)
