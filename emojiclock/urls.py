from django.http import HttpResponse
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
        font-size: 30em;
        font-size: 80vmin;
        text-align: center;
      }}
    </style>
  </head>
  <body>{}</body>
</html>
"""


def emojiclock(request):
    time = timezone.localtime().time()
    emoji = time_to_emoji(time)
    return HttpResponse(PAGE_TEMPLATE.format(emoji))


urlpatterns = [
    path('', emojiclock, name='home'),
]
