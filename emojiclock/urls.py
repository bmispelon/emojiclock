from http import HTTPStatus

from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.utils import timezone

from .utils import time_to_emoji

FULL_PAGE_EMOJI_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <style type="text/css">
      body {{
        font-size: 200px;
        text-align: center;
        line-height: 100vh;
      }}
    </style>
    <title>{emoji}</title>
  </head>
  <body>{emoji}</body>
  <!-- Questions, issues? https://github.com/bmispelon/emojiclock -->
</html>
""".strip()


class EmojiResponse:
    def __init__(self, emoji):
        self.emoji = emoji

    def as_html(self, *args, **kwargs):
        html = FULL_PAGE_EMOJI_TEMPLATE.format(emoji=self.emoji)
        return HttpResponse(html, *args, **kwargs)

    def as_json(self, *args, **kwargs):
        data = {'time': self.emoji}
        return JsonResponse(data, *args, **kwargs)

    def as_plaintext(self, *args, **kwargs):
        kwargs.setdefault('content_type', 'text/plain; charset=utf-8')
        return HttpResponse(self.emoji, *args, **kwargs)

    def as_appropriate_response(self, request, *args, **kwargs):
        SUPPORTED_CONTENT_TYPES = {
            # XXX Order is significant: first accepted contenttype is returned
            'text/html': self.as_html,
            'application/json': self.as_json,
            'text/plain': self.as_plaintext,
        }
        for contenttype, method in SUPPORTED_CONTENT_TYPES.items():
            if request.accepts(contenttype):
                return method(*args, **kwargs)

        return HttpResponse(
            '\N{SHRUG}',
            content_type='text/plain; charset=utf-8',
            status=HTTPStatus.NOT_ACCEPTABLE
        )

    @classmethod
    def from_request(cls, request, emoji, *args, **kwargs):
        return cls(emoji).as_appropriate_response(request, *args, **kwargs)


class TimeEmojiResponse(EmojiResponse):
    def __init__(self, time):
        emoji = time_to_emoji(time)
        super().__init__(emoji)


def emojiclock(request):
    return TimeEmojiResponse.from_request(request, timezone.localtime().time())


def handler500(request):
    emoji = '\N{POLICE CARS REVOLVING LIGHT}'
    return EmojiResponse.from_request(request, emoji, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def handler404(request, *args, **kwargs):
    emoji = '\N{GHOST}'
    return EmojiResponse.from_request(request, emoji, status=HTTPStatus.NOT_FOUND)


urlpatterns = [
    path('', emojiclock, name='home'),

    path('_500/', handler500),
    path('_404/', handler404),
]
