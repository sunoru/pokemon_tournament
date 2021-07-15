from django.urls import re_path
import accounts.views

app_name = 'accounts'
urlpatterns = [
    re_path(r'^$', accounts.views.home, name='home'),

    re_path(r'^tournaments/$', accounts.views.tournaments, name='tournaments'),
    re_path(r'^playerusers/$', accounts.views.playerusers, name='playerusers'),
    re_path(r'^login/$', accounts.views.login_view, name='login'),
    re_path(r'^logout/$', accounts.views.logout_view, name='logout'),
    re_path(r'^create/$', accounts.views.create, name='create'),
    re_path(r'^load/$', accounts.views.load, name='load'),
    re_path(r'^edit/$', accounts.views.edit, name='edit'),
    re_path(r'^edit/(?P<player_id>.+?)/$', accounts.views.player_setting, name='player_setting'),
    re_path(r'^(?P<player_id>.+?)/$', accounts.views.player_view, name='player_view'),
    re_path(r'^(?P<player_id>.+?)/logs$', accounts.views.player_logs, name='player_view'),
]
