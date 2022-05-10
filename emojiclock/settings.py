from environs import Env

env = Env()

@env.parser_for('secure_ssl_header')
def _(value):
    if not value:
        return None
    return value, 'https'


with env.prefixed('DJANGO_'):
    DEBUG = env.bool('DEBUG', default=True)
    SECRET_KEY = env.str('SECRET_KEY', default='asdf')
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
    CACHES = {'default': env.dj_cache_url('CACHE_URL', default='dummy://')}
    SECURE_PROXY_SSL_HEADER = env.secure_ssl_header('SECURE_PROXY_SSL_HEADER', default=None)

INSTALLED_APPS = ['django.contrib.sessions']
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'emojiclock.middlewares.timezone_middleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'emojiclock.urls'
WSGI_APPLICATION = 'emojiclock.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Oslo'
USE_I18N = False
USE_L10N = False
USE_TZ = True
