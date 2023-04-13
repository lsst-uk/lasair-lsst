"""lasair URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as authviews
from django.urls import include, path
from django.views.generic import TemplateView

from lasair import views
from lasair.utils import fits

from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),

    path('admin/', admin.site.urls),
    path('fits/<slug:candid_cutoutType>/', fits, name='fits'),
    path('', include('lasairapi.urls')),
    path('', include('lasair.apps.annotator.urls')),
    path('', include('lasair.apps.db_schema.urls')),
    path('', include('lasair.apps.filter_query.urls')),
    path('', include('lasair.apps.multimessenger_map.urls')),
    path('', include('lasair.apps.object.urls')),
    path('', include('lasair.apps.search.urls')),
    path('', include('lasair.apps.status.urls')),
    path('', include('lasair.apps.watchlist.urls')),
    path('', include('lasair.apps.watchmap.urls')),
    path('', include('users.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]


# ADD DJANGO DEBUG TOOLBAR
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
