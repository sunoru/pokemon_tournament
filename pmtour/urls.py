from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'pmtour.views.home', name='home'),
    url(r'^check/$', 'pmtour.views.check', name='check'),
    url(r'^bracket/$', 'pmtour.views.bracket', name='bracket'),
    url(r'^standings/$', 'pmtour.views.standings', name='standings'),
    url(r'^discussion/$', 'pmtour.views.discussion', name='discussion'),
    url(r'^log/$', 'pmtour.views.log', name='log'),
    url(r'^log/(?P<turn_number>\d+?)/bracket/$', 'pmtour.views.get_bracket', name='get_bracket'),
    url(r'^log/(?P<turn_number>\d+?)/standings/$', 'pmtour.views.get_standings', name='get_standings'),
    url(r'^settings/$', 'pmtour.views.settings', name='settings'),
    url(r'^settings/get_turns/$', 'pmtour.views.get_turns', name='get_turns'),
    url(r'^settings/get_elims/$', 'pmtour.views.get_elims', name='get_elims'),
    url(r'^participants/$', 'pmtour.views.participants', name='participants'),
    url(r'^participants/add/$', 'pmtour.views.add_player', name='add_player'),
    url(r'^delete/$', 'pmtour.views.delete', name='delete'),
)
