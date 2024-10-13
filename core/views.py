from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, filters
from algoliasearch_django import raw_search
from .models import Platform, Tag, LearningResource
from .serializers import PlatformSerializer, TagSerializer, LearningResourceSerializer


class PlatformListCreateView(generics.ListCreateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    http_method_names = ['get']

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']

class LearningResourceListCreateView(generics.ListCreateAPIView):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer
    http_method_names = ['get', 'post']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class LearningResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'put', 'delete']


def search_learning_resources(request):
    query = request.GET.get('q', '')
    params = {"hitsPerPage": 10}
    if query:
        response = raw_search(LearningResource, query, params)
        results = response.get('hits', [])
    else:
        results = []

    return JsonResponse(
        {
            'query': query, 
            'length': len(results),
            'results': results
        }, status=200)
