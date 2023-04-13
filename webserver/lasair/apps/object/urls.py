from . import views
from django.urls import path
from django.views.generic import RedirectView


urlpatterns = [
    path('objects/<slug:objectId>/', views.object_detail, name='object_detail'),
    path('object/<slug:objectId>/', RedirectView.as_view(pattern_name='object_detail', permanent=False))
]
