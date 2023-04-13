from . import views
from django.urls import path

urlpatterns = [
    path('watchlists/', views.watchlist_index, name='watchlist_index'),
    path('watchlists/<int:wl_id>/', views.watchlist_detail, name='watchlist_detail'),
    path('watchlists/<int:wl_id>/cat/', views.watchlist_download, name='watchlist_download'),
    path('watchlists/<int:wl_id>/delete/', views.watchlist_delete, name='watchlist_delete')
]
