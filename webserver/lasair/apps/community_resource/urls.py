from . import views
from django.urls import path

urlpatterns = [
    path('comres/', views.community_resource_index, name='community_resource_index')
]
