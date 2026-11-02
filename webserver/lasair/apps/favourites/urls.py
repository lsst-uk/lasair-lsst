from . import views
from django.urls import path

urlpatterns = [
    path('objects/<int:diaObjectId>/mark/', views.object_mark, name='object_mark'),
    path('favourites/', views.favourites_list, name='favourites'),
    path('hidden/', views.hidden_list, name='hidden_objects'),
    path('hidden/unhide-all/', views.unhide_all, name='unhide_all'),
]
