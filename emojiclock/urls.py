from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse,
)
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


def _emojiresponse(emoji, response_class=HttpResponse):
    body = FULL_PAGE_EMOJI_TEMPLATE.format(emoji=emoji)
    return response_class(body)


def emojiclock(request):
    time = timezone.localtime().time()
    emoji = time_to_emoji(time)

    if 'json' in request.META['HTTP_ACCEPT']:
        response = JsonResponse({'time': emoji})
    elif 'html' not in request.META['HTTP_ACCEPT']:
        response = HttpResponse(emoji, content_type='text/plain; charset=utf-8')
    else:
        response = _emojiresponse(emoji=emoji)

    return response


def handler500(request, *args, **kwargs):  # Not sure what arguments it should accept
    return _emojiresponse('\N{POLICE CARS REVOLVING LIGHT}', response_class=HttpResponseServerError)


def handler404(request, *args, **kwargs):
    return _emojiresponse('\N{GHOST}', response_class=HttpResponseNotFound)


urlpatterns = [
    path('', emojiclock, name='home'),

    path('_500/', handler500),
    path('_404/', handler404),
]
