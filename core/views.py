from rest_framework import generics, permissions, filters
from .models import DigitalLearningResourcePlatform, DigitalLearningResourceCategory, DigitalLearningResource
from .serializers import DigitalLearningResourcePlatformSerializer, DigitalLearningResourceCategorySerializer, DigitalLearningResourceSerializer


class DigitalLearningResourcePlatformListCreateView(generics.ListCreateAPIView):
    queryset = DigitalLearningResourcePlatform.objects.all()
    serializer_class = DigitalLearningResourcePlatformSerializer
    http_method_names = ['get']

class DigitalLearningResourceCategoryListCreateView(generics.ListCreateAPIView):
    queryset = DigitalLearningResourceCategory.objects.all()
    serializer_class = DigitalLearningResourceCategorySerializer
    http_method_names = ['get']

class DigitalLearningResourceListCreateView(generics.ListCreateAPIView):
    queryset = DigitalLearningResource.objects.all()
    serializer_class = DigitalLearningResourceSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'extra_data__summary']

class DigitalLearningResourceDetailView(generics.RetrieveDestroyAPIView):
    queryset = DigitalLearningResource.objects.all()
    serializer_class = DigitalLearningResourceSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'put', 'delete']


