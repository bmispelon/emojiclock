from datetime import time
import unicodedata

from django.test import override_settings, SimpleTestCase

import requests
import responses

from emojiclock.ip_to_timezone import ip_to_timezone, logger
from emojiclock.utils import time_to_emoji, emoji_to_time


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
        self.assertRegex(
            logged.output[0],
            f'^ERROR:{logger.name}:Response doesn\'t appear to be valid JSON'
        )
        self.assertEqual(tz, None)

    @responses.activate
    def test_unexpected_json_structure(self):
        responses.get('https://ipapi.co/192.0.2.0/json', json={'TIMEZONE': 'UTC'})
        with self.assertLogs(logger, level='ERROR') as logged:
            tz = ip_to_timezone('192.0.2.0')
        self.assertEqual(len(logged.output), 1)
        self.assertRegex(
            logged.output[0],
            f'^ERROR:{logger.name}:Response JSON content has an unexpected structure'
        )
        self.assertEqual(tz, None)


class EmojiTestCase(SimpleTestCase):
    def test_time_to_emoji(self):
        testdata = [
            (time(1), '\N{CLOCK FACE ONE OCLOCK}'),
            (time(1, 30), '\N{CLOCK FACE ONE-THIRTY}'),
            (time(13), '\N{CLOCK FACE ONE OCLOCK}'),
            (time(1, 14), '\N{CLOCK FACE ONE OCLOCK}'),
            (time(1, 15), '\N{CLOCK FACE ONE OCLOCK}'),
            (time(1, 15, 1), '\N{CLOCK FACE ONE-THIRTY}'),
            (time(1, 15, microsecond=1), '\N{CLOCK FACE ONE-THIRTY}'),
            (time(1, 16), '\N{CLOCK FACE ONE-THIRTY}'),
            (time(0), '\N{CLOCK FACE TWELVE OCLOCK}'),
            (time(12), '\N{CLOCK FACE TWELVE OCLOCK}'),
            (time(11, 59), '\N{CLOCK FACE TWELVE OCLOCK}'),
        ]
        for t, expected in testdata:
            with self.subTest(time=t):
                self.assertEqual(time_to_emoji(t), expected)

    def test_emoji_to_time(self):
        testdata = [
            ('\N{CLOCK FACE ONE OCLOCK}', time(1)),
            ('\N{CLOCK FACE ONE-THIRTY}', time(1, 30)),
            ('\N{CLOCK FACE TWELVE OCLOCK}', time(0)),
            ('\N{CLOCK FACE TWELVE-THIRTY}', time(0, 30)),
        ]
        for emoji, expected in testdata:
            with self.subTest(emoji=f'\\N{{{unicodedata.name(emoji)}}}'):
                self.assertEqual(emoji_to_time(emoji), expected)
