from django.http import JsonResponse
from haystack.query import SearchQuerySet


def autocomplete(request):
    """Autocomplete view specially formatted for jqueryui-autocomplete."""
    query = request.GET.get('term', '')
    if query:
        sqs = SearchQuerySet().autocomplete(content_auto=query)[:10]
    else:
        sqs = ()
    data = [{'label': result.text, 'value': result.url} for result in sqs]
    return JsonResponse(data, safe=False)
