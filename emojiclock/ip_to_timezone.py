import logging

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)


def ip_to_timezone(ip):
    """
    Query an external API to get the name of the timezone corresponding to the
    given IP address.
    """
    LOCAL_IPS = {'127.0.0.1'}

    if ip in LOCAL_IPS:
        return timezone.get_current_timezone_name()

    logger.info('Uncached timezone query for IP %s', ip)
    try:
        response = requests.get(f'https://ipapi.co/{ip}/json', timeout=10)
    except requests.Timeout:
        logger.exception("External query timed out")
        return None

    if response.status_code != requests.codes.ok:
        logger.error("External query returned error code %s", response.status_code)
        return None

    try:
        return response.json()['timezone']
    except requests.JSONDecodeError:
        logger.exception("Response doesn't appear to be valid JSON")
        return None
    except KeyError:
        logger.exception("Response JSON content has an unexpected structure")
        return None
