from django.conf.urls import patterns, include, url
from django.contrib import admin
#from pmtour import views
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'pmtour.views.index', name='index'),
    url(r'^django_admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^(?P<tour_id>.+)/', include('pmtour.urls', namespace='tournament')),
)
