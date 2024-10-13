# index.py

import algoliasearch_django as algoliasearch

from .models import LearningResource

algoliasearch.register(LearningResource)
