from django.http import JsonResponse
from haystack.query import SearchQuerySet


def autocomplete(request):
    query = request.GET.get('q', '')
    if query:
        sqs = SearchQuerySet().autocomplete(content_auto=query)[:10]
        suggestions = [result.text for result in sqs]
    else:
        suggestions = ()
    data = {
        'results': suggestions,
    }
    return JsonResponse(data)
