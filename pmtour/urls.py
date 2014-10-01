from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'pmtour.views.home', name='home'),
    url(r'^admin/$', 'pmtour.views.admin', name='admin')
)
