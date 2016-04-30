from django.conf.urls import patterns, include, url
import accounts.views

urlpatterns = patterns(
    '',
    url(r'^$', accounts.views.home, name='home'),

    url(r'^tournaments/$', accounts.views.tournaments, name='tournaments'),
    url(r'^playerusers/$', accounts.views.playerusers, name='playerusers'),
    url(r'^login/$', accounts.views.login_view, name='login'),
    url(r'^logout/$', accounts.views.logout_view, name='logout'),
    url(r'^create/$', accounts.views.create, name='create'),
    url(r'^load/$', accounts.views.load, name='load'),
    url(r'^edit/$', accounts.views.edit, name='edit'),
    url(r'^edit/(?P<player_id>.+?)/$', accounts.views.player_setting, name='player_setting'),
    url(r'^(?P<player_id>.+?)/$', accounts.views.player_view, name='player_view'),
    url(r'^(?P<player_id>.+?)/logs$', accounts.views.player_logs, name='player_view'),
)
