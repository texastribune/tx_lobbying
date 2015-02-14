from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView, TemplateView

from . import search_views
from . import views


urlpatterns = patterns('',
    url(r'^$', views.Landing.as_view(),
        name="home"),
    url(r'^about/$',
        TemplateView.as_view(template_name='tx_lobbying/about.html'), name='about'),
    url(r'^(?P<year>\d{4})/$', views.YearLanding.as_view(),
        name='year_landing'),
    url(r'^lobbyists/$', views.LobbyistList.as_view(),
        name="lobbyist_list"),
    url(r'^lobbyist/$', RedirectView.as_view(url='../lobbyists/')),
    url(
        r'^lobbyist/(?P<slug>\d+)/',
        include(patterns('',
            url(r'^$', views.LobbyistDetail.as_view(),
                name='lobbyist_detail'),
            url(r'^covers/$', views.LobbyistDetail.as_view(
                template_name='tx_lobbying/lobbyist_covers.html'),
                name='lobbyist_covers'),
            url(r'^cover/$', RedirectView.as_view(url='../covers/')),
            url(r'^cover/(?P<report_id>\d+)/$', views.CoversheetDetail.as_view(),
                name='coversheet_detail'),
        ))
    ),
    url(r'^registration/(?P<repno>\d+)/$', views.RegistrationDetail.as_view(),
        name='registration_detail'),
    url(r'^interests/$', views.InterestList.as_view(),
        name='interest_list'),
    url(r'^interest/$', RedirectView.as_view(url='../interests/')),
    url(r'^interest/(?P<pk>\d+)/$', views.InterestDetail.as_view(),
        name='interest_detail'),
    url(r'^addresses/$', views.AddressList.as_view(),
        name="address_list"),
    url(r'^address/$', RedirectView.as_view(url='../addresses/')),
    url(r'^address/(?P<pk>\d+)/$', views.AddressDetail.as_view(),
        name='address_detail'),
    url(r'^address/(?P<pk>\d+)/geocode/$', views.AddressGeocode.as_view(),
        name='address_geocode'),
    url(r'^subject/$', RedirectView.as_view(url='../subjects/')),
    url(r'^subjects/$', views.SubjectList.as_view(),
        name='subject_list'),
    url(r'^subject/(?P<slug>[-\w]*)/$', views.SubjectDetail.as_view(),
        name='subject_detail'),

    url(r'^search/ac/', search_views.autocomplete, name='autocomplete'),

    # for debugging
    url(r'^_style/$',
        TemplateView.as_view(template_name='tx_lobbying/styleguide.html')),
)
