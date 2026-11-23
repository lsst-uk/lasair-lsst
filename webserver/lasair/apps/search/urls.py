from . import views
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path('simple_search', RedirectView.as_view(pattern_name='filter_query_create', permanent=False)),
    path('search/', views.search, name='search'),
    path('search/<query>', views.search, name='search'),
]
