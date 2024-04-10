from . import views
from django.urls import path

urlpatterns = [
    path('mma_watchmaps/', views.mma_watchmap_index, name='mma_watchmap_index'),
    path('mma_watchmaps/<int:mw_id>/', views.mma_watchmap_detail, name='mma_watchmap_detail'),
#    path('mma_watchmaps/<int:mw_id>/file/', views.mma_watchmap_download, name='mma_watchmap_download'),
]
