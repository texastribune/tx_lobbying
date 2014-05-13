from django.db.models import Count, Sum
from django.views.generic import DetailView, ListView, TemplateView

from .models import (Lobbyist, Coversheet, ExpenseDetailReport)
from . import models


class Landing(TemplateView):
    template_name = "tx_lobbying/landing.html"
    years = range(2005, 2015)

    def aggregate_covers(self):
        data = (
            Coversheet.objects.all().values('year')
            .annotate(
                Count('pk'),
                Sum('spent_guess'),
                Sum('transportation'),
                Sum('food'),
                Sum('entertainment'),
                Sum('gifts'),
                Sum('awards'),
                Sum('events'),
                Sum('media'),
                # missing no. of registered lobbyists
                # missing no. of lobbyists that actually spent
                # missing no. that actually had details
            )
            .order_by('year')
        )
        # fill in missing data
        for row in data:
            year = row['year']
            qs = Coversheet.objects.filter(year=year)
            row['itemized'] = qs.exclude(details__isnull=True).count()
            row['registered'] = Lobbyist.objects.filter(
                registrations__year__exact=year).distinct().count()
            row['spent_anything'] = Lobbyist.objects.filter(
                stats__year__exact=year, stats__spent_guess__gt=0).distinct().count()
        return data

    def aggregate_details(self):
        facets = ['food', 'entertainment', 'gift', 'award']
        data = dict()
        for year in self.years:
            qs = ExpenseDetailReport.objects.filter(year=year)
            year_data = {}
            total = 0
            count = 0
            for facet in facets:
                year_data[facet] = qs.filter(type=facet).\
                    aggregate(sum=Sum('amount_guess'), count=Count('amount_guess'))
                total += year_data[facet]['sum'] or 0
                count += year_data[facet]['count'] or 0
            year_data['total'] = total
            year_data['count'] = count  # same as qs.count()
            data[year] = year_data
        return data

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data(**kwargs)
        context['spending_summary'] = self.aggregate_covers()
        context['itemized'] = self.aggregate_details()
        return context


class YearLanding(TemplateView):
    template_name = "tx_lobbying/year_landing.html"

    def get_top_lobbyists(self, count=20):
        qs = (models.LobbyistStats.objects.filter(year=self.year)
            .select_related('lobbyist')
            .order_by('-spent_guess')[:count])
        return qs

    def get_top_interests(self, count=20):
        qs = (models.InterestStats.objects
            .filter(year=self.year, interest__canonical__isnull=True)
            .select_related('interest')
            .order_by('-high')[:count])
        return qs

    def get_context_data(self, **kwargs):
        self.year = kwargs['year']
        context = super(YearLanding, self).get_context_data(**kwargs)
        context['top_lobbyists'] = self.get_top_lobbyists()
        context['top_interests'] = self.get_top_interests()
        return context


class LobbyistList(ListView):
    queryset = (Lobbyist.objects.all().order_by('sort_name')
        .annotate(spent=Sum('coversheets__spent_guess'))
        # .filter(spent__gt=0)
    )


class LobbyistDetail(DetailView):
    queryset = Lobbyist.objects.all().prefetch_related(
        'years__compensation_set__interest', 'coversheets__details')
    slug_field = 'filer_id'


class CoversheetDetail(DetailView):
    queryset = models.Coversheet.objects.select_related('subjects')
    slug_field = 'report_id'
    slug_url_kwarg = 'report_id'


class InterestList(ListView):
    queryset = (models.Interest.objects.filter(canonical__isnull=True)
        .prefetch_related('aliases'))


class InterestDetail(DetailView):
    model = models.Interest

    def get_context_data(self, **kwargs):
        data = super(InterestDetail, self).get_context_data(**kwargs)
        data['aliases'] = (self.object.aliases.all())
        data['compensation_set'] = (self.object.compensation_set_massive
            .prefetch_related('interest', 'annum__lobbyist')
            .order_by('annum__lobbyist', 'annum__year'))
        return data


class AddressList(ListView):
    queryset = models.Address.objects.all().order_by('address1', 'zipcode')


class AddressDetail(DetailView):
    model = models.Address

    def get_context_data(self, **kwargs):
        data = super(AddressDetail, self).get_context_data(**kwargs)
        data['registration_reports'] = (
            models.RegistrationReport.objects.filter(address=self.object)
            .select_related('lobbyist')
            .order_by('lobbyist', 'year'))
        return data
