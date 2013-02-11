from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.Landing.as_view(),
        name="home"),
    url(r'^lobbyists/$', views.LobbyistList.as_view(),
        name="lobbyist_list"),
    url(r'^lobbyist/(?P<slug>\d+)/$', views.LobbyistDetail.as_view(),
        name="lobbyist_detail"),
)
