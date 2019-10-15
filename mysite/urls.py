from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
import django.contrib.staticfiles.views as static_views
from django.views.generic.base import RedirectView
import mysite.views
import accounts.urls
import pmtour.urls

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', mysite.views.index, name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True), name='favicon'),
    url(r'^django_admin/', include(admin.site.urls)),
    url(r'^accounts/', include(accounts.urls, namespace='accounts')),
    url(r'^(?P<tour_id>.+?)/', include(pmtour.urls, namespace='tournament')),
)
if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', static_views.serve)
    ]
