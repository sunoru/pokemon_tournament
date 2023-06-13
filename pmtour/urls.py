from django.urls import re_path
import pmtour.views

app_name = 'pmtour'

urlpatterns = [
    re_path(r'^$', pmtour.views.home, name='home'),
    re_path(r'^check/$', pmtour.views.check_status, name='check'),
    re_path(r'^bracket/$', pmtour.views.bracket, name='bracket'),
    re_path(r'^standings/$', pmtour.views.standings, name='standings'),
    re_path(r'^discussion/$', pmtour.views.discussion, name='discussion'),
    re_path(r'^log/$', pmtour.views.log, name='log'),
    re_path(r'^log/(?P<turn_number>\d+?)/bracket/$', pmtour.views.log_bracket, name='get_bracket'),
    re_path(r'^log/(?P<turn_number>\d+?)/standings/$', pmtour.views.log_standings, name='get_standings'),
    re_path(r'^settings/$', pmtour.views.settings, name='settings'),
    re_path(r'^settings/get_turns/$', pmtour.views.get_turns, name='get_turns'),
    re_path(r'^settings/get_elims/$', pmtour.views.get_elims, name='get_elims'),
    re_path(r'^participants/$', pmtour.views.participants, name='participants'),
    re_path(r'^participants/add/$', pmtour.views.add_player, name='add_player'),
    re_path(r'^participants/add_test/$', pmtour.views.add_test_player, name='add_test_player'),
    re_path(r'^participants/edit_name/$', pmtour.views.edit_name, name='edit_name'),
    re_path(r'^export/$', pmtour.views.export, name='export'),
    re_path(r'^delete/$', pmtour.views.delete, name='delete'),

    # Advanced settings
    re_path(r'^advanced/$', pmtour.views.advanced, name='advanced'),
    re_path(r'^bye_rounds/$', pmtour.views.bye_rounds, name='bye_rounds'),
]
