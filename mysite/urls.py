from django.conf import settings
from django.urls import re_path, include
from django.contrib import admin
import django.contrib.staticfiles.views as static_views
from django.views.generic.base import RedirectView
import mysite.views
import accounts.urls
import pmtour.urls

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', mysite.views.index, name='index'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True), name='favicon'),
    re_path(r'^django_admin/', admin.site.urls),
    re_path(r'^accounts/', include(accounts.urls, namespace='accounts')),
    re_path(r'^(?P<tour_id>.+?)/', include(pmtour.urls, namespace='tournament')),
]
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', static_views.serve)
    ]
