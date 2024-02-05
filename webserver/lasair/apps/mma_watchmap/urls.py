from . import views
from django.urls import path

urlpatterns = [
    path('mma_watchmaps/', views.mma_watchmap_index, name='mma_watchmap_index'),
    path('mma_watchmaps/<int:ar_id>/', views.mma_watchmap_detail, name='mma_watchmap_detail'),
    path('mma_watchmaps/<int:ar_id>/file/', views.mma_watchmap_download, name='mma_watchmap_download'),
    path('mma_watchmaps/<int:ar_id>/delete/', views.mma_watchmap_delete, name='mma_watchmap_delete')
]
