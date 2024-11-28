from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('platforms/', views.PlatformListCreateView.as_view(), name='platforms'),
    path('tags/', views.TagListCreateView.as_view(), name='tags'),
    path('learning-resources/', views.LearningResourceListCreateView.as_view(), name='learning_resources'),
    path('learning-resources/<uuid:id>/', views.LearningResourceDetailView.as_view(), name='learning_resource_detail'),
    path('search/', views.search_learning_resources, name='search'),


    # Landing page
    path('', TemplateView.as_view(template_name="core/index.html"), name='index'),
]
