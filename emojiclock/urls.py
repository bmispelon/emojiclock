from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.utils import timezone

from .utils import time_to_emoji


PAGE_TEMPLATE = """
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
    <title>{clock}</title>
  </head>
  <body>{clock}</body>
  <!-- Questions, issues? https://github.com/bmispelon/emojiclock -->
</html>
"""


def emojiclock(request):
    time = timezone.localtime().time()
    emoji = time_to_emoji(time)

    if 'json' in request.META['HTTP_ACCEPT']:
        response = JsonResponse({'time': emoji})
    elif 'html' not in request.META['HTTP_ACCEPT']:
        response = HttpResponse(emoji, content_type='text/plain; charset=utf-8')
    else:
        response = HttpResponse(PAGE_TEMPLATE.format(clock=emoji))

    return response


urlpatterns = [
    path('', emojiclock, name='home'),
]
