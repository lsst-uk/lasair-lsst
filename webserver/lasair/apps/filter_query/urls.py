from . import views
from django.urls import path

urlpatterns = [
    path('filters/', views.filter_query_index, name='filter_query_index'),
    path('filters/create/', views.filter_query_create, name='filter_query_create'),
    path('filters/<int:mq_id>/delete/', views.filter_query_delete, name='filter_query_delete'),
    path('filters/<int:mq_id>/update/', views.filter_query_create, name='filter_query_update'),
    path('filters/<int:mq_id>/', views.filter_query_detail, name='filter_query_detail'),
    path('filters/<int:mq_id>/<slug:action>/', views.filter_query_detail, name='filter_query_detail_run'),
    path('filters/log/<slug:topic>/', views.filter_query_log, name='filter_query_log'),

]
