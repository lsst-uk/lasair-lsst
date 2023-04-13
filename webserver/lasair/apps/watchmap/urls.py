from . import views
from django.urls import path

urlpatterns = [
    path('watchmaps/', views.watchmap_index, name='watchmap_index'),
    path('watchmaps/<int:ar_id>/', views.watchmap_detail, name='watchmap_detail'),
    path('watchmaps/<int:ar_id>/file/', views.watchmap_download, name='watchmap_download'),
    path('watchmaps/<int:ar_id>/delete/', views.watchmap_delete, name='watchmap_delete')
]
