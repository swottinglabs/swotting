# index.py

import algoliasearch_django as algoliasearch
from django.conf import settings
from .models import LearningResource

class LearningResourceIndex(algoliasearch.AlgoliaIndex):
    fields = [
        'name', 
        'short_description', 
        'description', 
        'is_free', 
        'platform_course_id',
        'url',
        'platform_last_update',
        'platform_reviews_rating',
        'platform_reviews_count'
    ]
    geo_field = None
    settings = {
        'searchableAttributes': [
            'name',
            'short_description',
            'description'
        ],
        'attributesForFaceting': [
            'is_free',
            'platform_id'
        ]
    }
    index_name = 'learning_resource'
    
    # This automatically adds the prefix from settings to the index name
    # So the actual index name will be: {prefix}learning_resource
    # For example: heiko_local_learning_resource

algoliasearch.register(LearningResource, LearningResourceIndex)
