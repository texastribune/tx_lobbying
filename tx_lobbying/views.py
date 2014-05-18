from itertools import groupby
from operator import itemgetter

from django.db.models import Count, Sum
from django.http import HttpResponseBadRequest, JsonResponse
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
        n_itemized = {
            x['year']: x['pk__count'] for x in
            (Coversheet.objects.exclude(details__isnull=True)
            .order_by('year').values('year')
            .annotate(Count('pk')))
        }
        n_spent = {
            x['stats__year']: x['pk__count'] for x in
            (Lobbyist.objects.filter(stats__spent_guess__gt=0).distinct()
            .order_by('stats__year')
            .values('stats__year')
            .annotate(Count('pk')))
        }
        for row in data:
            year = row['year']
            row['itemized'] = n_itemized.get(year)
            # can't do the same trick because orm does an outer join
            row['registered'] = Lobbyist.objects.filter(
                registrations__year__exact=year).distinct().count()
            row['spent_anything'] = n_spent.get(year)
        return data

    def aggregate_details(self):
        def refactor(grouper):
            out = {
                x['type']: x
                for x in grouper
            }
            # meh on efficiency for now
            out['total'] = {
                'sum': sum(map(itemgetter('sum'), out.values())),
                'count': sum(map(itemgetter('count'), out.values())),
            }
            return out

        totals = (
            ExpenseDetailReport.objects.all().values('year', 'type')
            .annotate(sum=Sum('amount_guess'), count=Count('pk'))
            .order_by('year')
        )
        data = groupby(totals, key=itemgetter('year'))
        data = [(year, refactor(grouper)) for year, grouper in data]
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

    def get_context_data(self, **kwargs):
        data = super(LobbyistDetail, self).get_context_data(**kwargs)
        data['subject_list'] = (models.Subject.objects
            .filter(reports__lobbyist=self.object).distinct())
        return data


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
    queryset = (models.Address.objects
        .filter(canonical__isnull=True)
        .prefetch_related('aliases')
        .order_by('address1', 'zipcode'))


class AddressDetail(DetailView):
    model = models.Address

    def get_context_data(self, **kwargs):
        data = super(AddressDetail, self).get_context_data(**kwargs)
        # TODO build into the model
        if self.object.coordinate and int(self.object.coordinate_quality) < 4:
            # TODO only build aliases if the coordinate_quality is good enough
            data['aliases'] = (
                models.Address.objects
                .filter(coordinate__equals=self.object.coordinate)
            )
        else:
            data['aliases'] = False
        data['registration_reports'] = (
            models.RegistrationReport.objects.filter(address=self.object)
            .select_related('lobbyist')
            .order_by('lobbyist', 'year'))
        return data


class AddressGeocode(DetailView, JsonResponse):
    model = models.Address

    def get(self, request, *args, **kwargs):
        from .utils import geocode_address, GeocodeException
        self.object = self.get_object()
        try:
            geocode_address(self.object)
        except GeocodeException as e:
            return HttpResponseBadRequest(e)
        return JsonResponse({
            'latitude': self.object.coordinate.y,
            'longitude': self.object.coordinate.x,
            'title': '{}: {}'.format(
                self.object.coordinate_quality,
                self.object.coordinate_quality_label,
            ),
        })


class SubjectList(ListView):
    model = models.Subject


class SubjectDetail(DetailView):
    model = models.Subject

    def get_context_data(self, **kwargs):
        data = super(SubjectDetail, self).get_context_data(**kwargs)
        data['lobbyist_list'] = (models.Lobbyist.objects
            .filter(coversheets__subjects=self.object)
            .distinct())
        return data
