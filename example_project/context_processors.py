import os


def junk(request):
    """Context processor to put junk in the trunk."""
    settings = (
        'GA_TRACKING_ID',
    )
    return {x: os.environ.get(x, '') for x in settings}
