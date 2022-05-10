from functools import partial

from django.core.cache import cache as default_cache
from django.utils import timezone

from ipware import get_client_ip

from emojiclock.ip_to_timezone import ip_to_timezone


def get_timezone_name_for_ip(ip):
    """
    Return the name of the timezone corresponding to the given IP.

    Results are cached.
    """
    return default_cache.get_or_set(f'django-ip-tz-{ip}', partial(ip_to_timezone, ip))


def get_user_timezone(request):
    ip_address, _ = get_client_ip(request)
    if ip_address is not None:
        return get_timezone_name_for_ip(ip_address)

    return None


def timezone_middleware(get_response):
    """
    Store the user's timezone (based on IP address) in the session and activate
    it for every request.
    """
    def middleware(request):
        try:
            user_timezone = request.session['timezone']
        except KeyError:
            user_timezone = get_user_timezone(request)
            request.session['timezone'] = user_timezone

        if user_timezone is not None:
            timezone.activate(user_timezone)

        return get_response(request)

    return middleware
