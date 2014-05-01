from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from . import views


urlpatterns = patterns('',
    url(r'^$', views.Landing.as_view(),
        name="home"),
    url(r'^(?P<year>\d{4})/$', views.YearLanding.as_view(),
        name='year_landing'),
    url(r'^lobbyists/$', views.LobbyistList.as_view(),
        name="lobbyist_list"),
    url(r'^lobbyist/$', RedirectView.as_view(url='../lobbyists/')),
    url(r'^lobbyist/(?P<slug>\d+)/$', views.LobbyistDetail.as_view(),
        name="lobbyist_detail"),
    url(r'^interests/$', views.InterestList.as_view(),
        name='interest_list'),
    url(r'^interest/$', RedirectView.as_view(url='../interests/')),
    url(r'^interest/(?P<pk>\d+)/$', views.InterestDetail.as_view(),
        name='interest_detail'),
    url(r'^address/(?P<pk>\d+)/$', views.AddressDetail.as_view(),
        name='address_detail'),
)
