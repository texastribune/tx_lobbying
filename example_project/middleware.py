from django.utils.cache import patch_response_headers, get_max_age


class DefaultCacheHeadersMiddleware(object):
    """
    Add cache instruction headers to all responses unless explicitly specified.

    This uses the same settings as the rest of the cache middleware,
    (CACHE_MIDDLEWARE_SECONDS) but skips the actual caching. Intended for use
    with an upstream cache like Varnish.
    """
    def process_response(self, request, response):
        # TODO if cache length gets long (like over 10 minutes), set a shorter
        # cache time by default on those.
        #
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.3
        # if response.status_code == 302:
        #     return response

        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length inside patch_response_headers.
        timeout = get_max_age(response)
        patch_response_headers(response, timeout)
        return response
