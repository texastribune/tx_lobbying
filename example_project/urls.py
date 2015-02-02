from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^notebook/$',
        TemplateView.as_view(template_name='notebook.html'),
        name='notebook'),
    url(r'^', include('tx_lobbying.urls',
        namespace='tx_lobbying', app_name='tx_lobbying')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', TemplateView.as_view(
        content_type='text/plain', template_name='robots.txt')),
)
