from . import views
from django.urls import path

urlpatterns = [
    path('schema/', views.schema_index, name='schema_index'),
]
