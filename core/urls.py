from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('platforms', views.DigitalLearningResourcePlatformListCreateView.as_view(), name='platforms'),
    path('categories', views.DigitalLearningResourceCategoryListCreateView.as_view(), name='categories'),
    path('courses', views.DigitalLearningResourceListCreateView.as_view(), name='courses'),
    path('courses/<int:id>', views.DigitalLearningResourceDetailView.as_view(), name='course'),
    path('search', views.search_digital_learning_resources, name='search'),


    # Landing page
    path('join-waitlist/', views.join_waitlist, name='join_waitlist'),
    path('', TemplateView.as_view(template_name="core/index.html"), name='index'),
]
