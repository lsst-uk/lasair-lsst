from . import views
from django.urls import path

urlpatterns = [
    path('gw_maps/', views.gw_map_index, name='gw_map_index'),
    path('gw_maps/<skymap_id_version>/', views.gw_map_detail, name='gw_map_detail'),
]
