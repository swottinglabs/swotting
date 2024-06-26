# index.py

import algoliasearch_django as algoliasearch

from .models import DigitalLearningResource

algoliasearch.register(DigitalLearningResource)
