from . import views
from django.urls import path

urlpatterns = [
    path('annotators/', views.annotator_index, name='annotator_index'),
    path('annotators/<slug:topic>/', views.annotator_detail, name='annotator_detail'),
]
