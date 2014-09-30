from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'accounts.views.home', name='home'),

    url(r'^login/$', 'accounts.views.login_view', name='login'),
    url(r'^create/$', 'accounts.views.create', name='create'),
)
