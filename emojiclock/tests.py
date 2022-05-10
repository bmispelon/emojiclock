from unittest import mock

from django.test import override_settings, SimpleTestCase

import requests
import responses

from emojiclock.ip_to_timezone import ip_to_timezone, logger


class IPToTimezoneTestCase(SimpleTestCase):
    @override_settings(TIME_ZONE='UTC')
    def test_localhost(self):
        self.assertEqual(ip_to_timezone('127.0.0.1'), 'UTC')

    @responses.activate
    def test_external_ip(self):
        responses.get('https://ipapi.co/192.0.2.0/json', json={'timezone': 'UTC'})
        tz = ip_to_timezone('192.0.2.0')
        self.assertEqual(tz, 'UTC')

    @responses.activate
    def test_timeout(self):
        responses.get('https://ipapi.co/192.0.2.0/json', body=requests.Timeout("too slow"))
        with self.assertLogs(logger, level='ERROR') as logged:
            tz = ip_to_timezone('192.0.2.0')
        self.assertEqual(len(logged.output), 1)
        self.assertRegex(logged.output[0], f'^ERROR:{logger.name}:External query timed out')
        self.assertEqual(tz, None)

    @responses.activate
    def test_server_response_500(self):
        responses.get('https://ipapi.co/192.0.2.0/json', status=500)
        with self.assertLogs(logger, level='ERROR') as logged:
            tz = ip_to_timezone('192.0.2.0')
        self.assertEqual(logged.output, [
            f"ERROR:{logger.name}:External query returned error code 500",
        ])
        self.assertEqual(tz, None)

    @responses.activate
    def test_invalid_json_response(self):
        responses.get('https://ipapi.co/192.0.2.0/json', body='not valid json')
        with self.assertLogs(logger, level='ERROR') as logged:
            tz = ip_to_timezone('192.0.2.0')
        self.assertEqual(len(logged.output), 1)
        self.assertRegex(logged.output[0], f'^ERROR:{logger.name}:Response doesn\'t appear to be valid JSON')
        self.assertEqual(tz, None)

    @responses.activate
    def test_unexpected_json_structure(self):
        responses.get('https://ipapi.co/192.0.2.0/json', json={'TIMEZONE': 'UTC'})
        with self.assertLogs(logger, level='ERROR') as logged:
            tz = ip_to_timezone('192.0.2.0')
        self.assertEqual(len(logged.output), 1)
        self.assertRegex(logged.output[0], f'^ERROR:{logger.name}:Response JSON content has an unexpected structure')
        self.assertEqual(tz, None)
