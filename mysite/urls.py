from django.conf.urls import patterns, include, url
from django.contrib import admin
#from pmtour import views
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'pmtour.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<tour_id>.+)/', include('pmtour.urls', namespace='tournament')),
)
