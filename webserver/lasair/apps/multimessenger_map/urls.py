from . import views
from django.urls import path

urlpatterns = [
    path('mm_maps/', views.mm_map_index, name='mm_map_index'),
    path('mm_maps/<skymap_id_version>/', views.mm_map_detail, name='mm_map_detail'),
]
