from . import views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('simple_search', TemplateView.as_view(template_name='simple_search.html')),
    path('search/', views.search, name='search'),
    path('search/<query>', views.search, name='search'),
]
