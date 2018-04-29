from django.core.cache import cache as default_cache
from django.utils import timezone

from functools import partial
import logging

import requests

logger = logging.getLogger(__name__)


def _get_timezone_name_for_ip(ip):
    """
    Query an external API to get the name of the timezone corresponding to the
    given IP address.
    """
    LOCAL_IPS = {'127.0.0.1'}
    API_ENDPOINT = 'https://timezoneapi.io/api/ip/'

    if ip in LOCAL_IPS:
        params = {}  # This will make timezoneapi return information for our own ip address instead of 127.0.0.1
    else:
        params = {'ip': ip}

    logger.info('Uncached timezone query for IP %s', ip)
    response = requests.get(API_ENDPOINT, params=params)
    response.raise_for_status()

    try:
        return response.json()['data']['timezone']['id']
    except (KeyError, TypeError):
        return None


def get_timezone_name_for_ip(ip):
    """
    Return the name of the timezone corresponding to the given IP.

    Results are cached.
    """
    cachekey = 'django-ip-tz-{}'.format(ip)
    return default_cache.get_or_set(cachekey, partial(_get_timezone_name_for_ip, ip))


def get_client_ip(request):
    """
    Return the IP address of the client for the given request.

    If the IP address can't be found, return None.
    """
    if 'HTTP_X_FORWARDED_FOR' in request.META:  # For Heroku
        return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]

    if 'REMOTE_ADDR' in request.META:
        return request.META['REMOTE_ADDR']

    return None


def get_user_timezone(request):
    ip_address = get_client_ip(request)
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
