import cgi
import unicodedata
from datetime import time
from http import HTTPStatus

import lxml.html
import requests
import responses
import time_machine
from django.test import SimpleTestCase, override_settings

from emojiclock.ip_to_timezone import ip_to_timezone, logger
from emojiclock.utils import emoji_to_time, time_to_emoji


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


class ViewsTestCase(SimpleTestCase):
    def _assertResponseContentType(self, response, contenttype, status_code=HTTPStatus.OK):
        if status_code is not None:
            self.assertEqual(response.status_code, status_code)
        if contenttype is None:
            self.assertNotIn('Content-Type', response)
        else:
            self.assertIn('Content-Type', response)
            ct, _ = cgi.parse_header(response['Content-Type'])
            self.assertEqual(ct, contenttype)

    def test_response_content_types(self):
        testdata = [
            ('text/html', 'text/html'),
            ('text/plain', 'text/plain'),
            ('application/json', 'application/json'),
            ('*/*', 'text/html'),
        ]
        for client_accept, expected_response_contenttype in testdata:
            with self.subTest(contenttype=client_accept):
                response = self.client.get('/', HTTP_ACCEPT=client_accept)
                self._assertResponseContentType(response, expected_response_contenttype)

    def test_unsupported_content_type(self):
        response = self.client.get('/', HTTP_ACCEPT='video/mp4')
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    @time_machine.travel('2000-01-01 01:30')
    def test_output_json(self):
        response = self.client.get('/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.json(), {'time': '\N{CLOCK FACE ONE-THIRTY}'})

    @time_machine.travel('2000-01-01 01:30')
    def test_output_plaintext(self):
        response = self.client.get('/', HTTP_ACCEPT='text/plain')
        self.assertEqual(response.content, '\N{CLOCK FACE ONE-THIRTY}'.encode('utf8'))

    @time_machine.travel('2000-01-01 01:30')
    def test_output_html(self):
        response = self.client.get('/', HTTP_ACCEPT='text/html')
        tree = lxml.html.fromstring(response.content)
        self.assertEqual(tree.find('body').text, '\N{CLOCK FACE ONE-THIRTY}')

    @time_machine.travel('2000-01-01 01:30')
    def test_output_html_title(self):
        response = self.client.get('/', HTTP_ACCEPT='text/html')
        tree = lxml.html.fromstring(response.content)
        self.assertEqual(tree.find('head').find('title').text, '\N{CLOCK FACE ONE-THIRTY}')

    def test_html_is_trimmed(self):
        response = self.client.get('/', HTTP_ACCEPT='text/html')
        content = response.content.decode(response.charset)
        self.assertFalse(content[0].isspace())
        self.assertFalse(content[-1].isspace())
