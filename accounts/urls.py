from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'accounts.views.home', name='home'),

    url(r'^login$', 'accounts.views.login_view', name='login'),
    url(r'^logout$', 'accounts.views.logout_view', name='logout'),
    url(r'^create$', 'accounts.views.create', name='create'),
    url(r'^load$', 'accounts.views.load', name='load'),
    url(r'^edit/$', 'accounts.views.edit', name='edit'),
    url(r'^edit/(?P<player_id>.+?)$', 'accounts.views.player_setting', name='player_setting'),
)
