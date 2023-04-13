from . import views
from django.urls import path

urlpatterns = [
    path('status/', views.status_today, name='status_today'),
    path('status/<int:nid>/', views.status, name='status'),
]
