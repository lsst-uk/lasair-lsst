from . import views
from django.urls import path
from django.views.generic import RedirectView


urlpatterns = [
    path('objects/<slug:diaObjectId>/', views.object_detail, name='object_detail'),
    path('object/<slug:diaObjectId>/', RedirectView.as_view(pattern_name='object_detail', permanent=False))
]
