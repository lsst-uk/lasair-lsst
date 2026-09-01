from . import views
from django.urls import path

urlpatterns = [
    path('objects/<int:diaObjectId>/mark/', views.object_mark, name='object_mark'),
]
