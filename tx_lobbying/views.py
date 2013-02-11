from django.db.models import Sum
from django.views.generic import DetailView, ListView, TemplateView

from .models import (Lobbyist,
    ExpenseCoversheet)


class Landing(TemplateView):
    template_name = "tx_lobbying/landing.html"
    years = range(2005, 2014)

    def aggregate_covers(self):
        facets = ['transportation', 'food', 'entertainment', 'gifts', 'awards', 'events', 'media']
        data = dict()
        for year in self.years:
            qs = ExpenseCoversheet.objects.filter(year=year)
            year_data = qs.aggregate(*map(Sum, facets))
            year_data['total'] = sum(year_data.values())
            year_data['count'] = qs.count()
            data[year] = year_data
        return data

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data(**kwargs)
        context['covers'] = self.aggregate_covers()
        return context


class LobbyistList(ListView):
    queryset = Lobbyist.objects.all().order_by('sort_name')


class LobbyistDetail(DetailView):
    queryset = Lobbyist.objects.all()
    slug_field = 'filer_id'
