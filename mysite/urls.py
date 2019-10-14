from django.conf.urls import patterns, include, url
from django.contrib import admin
import django.shortcuts
import mysite.views

#from pmtour import views
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', mysite.views.index, name='index'),
    url(r'^favicon\.ico$', django.shortcuts.redirect, {'to': '/static/images/favicon.ico'}),
    url(r'^django_admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^(?P<tour_id>.+?)/', include('pmtour.urls', namespace='tournament')),
)
