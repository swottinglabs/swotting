from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import WaitlistForm
from rest_framework import generics, permissions, filters
from algoliasearch_django import raw_search
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


def join_waitlist(request):
    if request.method == "POST":
        form = WaitlistForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Subscription successful!'}, status=200)
        else:
            return JsonResponse({'message': 'Error joining waitlist!'}, status=400)
    else:
        form = WaitlistForm()
    return render(request, 'core/index.html', {'form': form})

# def search_digital_learning_resources(request):
#     query = request.GET.get('q', '')
#     params = {"hitsPerPage": 5}
#     if query:
#         response = raw_search(DigitalLearningResource, query, params)
#         print(response)
#         results = response.get('hits', [])
#     else:
#         results = []

#     return {'results': results, 'query': query}

def search_digital_learning_resources(request):
    query = request.GET.get('q', '')
    params = {"hitsPerPage": 10}
    if query:
        response = raw_search(DigitalLearningResource, query, params)
        results = response.get('hits', [])
    else:
        results = []

    return JsonResponse(
        {
            'query': query, 
            'length': len(results),
            'results': results
        }, status=200)

