from rest_framework import serializers
from .models import DigitalLearningResourcePlatform, DigitalLearningResourceCategory, DigitalLearningResource

class DigitalLearningResourcePlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalLearningResourcePlatform
        fields = '__all__'

class DigitalLearningResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalLearningResourceCategory
        fields = '__all__'


class DigitalLearningResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalLearningResource
        fields = '__all__'

