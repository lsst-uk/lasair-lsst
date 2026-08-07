from . import views
from django.urls import path

urlpatterns = [
    path('annotators/', views.annotator_index, name='annotator_index'),
    path('annotators/<slug:topic>/', views.annotator_detail, name='annotator_detail'),

    path('tags/', views.tags_index, name='tags_index'),
    path('tags/addtag/<int:diaObjectId>/<username>/<tag>/', views.addtag, name='tags.addtag'),
    path('tags/removetag/<int:diaObjectId>/<username>/<tag>/', views.removetag, name='tags.removetag'),
]
