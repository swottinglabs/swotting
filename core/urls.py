from django.urls import path
from . import views

urlpatterns = [
    path('platforms', views.DigitalLearningResourcePlatformListCreateView.as_view(), name='platforms'),
    path('categories', views.DigitalLearningResourceCategoryListCreateView.as_view(), name='categories'),
    path('courses', views.DigitalLearningResourceListCreateView.as_view(), name='courses'),
    path('courses/<int:id>', views.DigitalLearningResourceDetailView.as_view(), name='course'),
]