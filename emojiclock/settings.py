"""
Django settings for emojiclock project.

Generated by 'django-admin startproject' using Django 2.0b1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os

ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'dev').lower()


if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
    ALLOWED_HOSTS = ['emojiclock.herokuapp.com']
elif ENVIRONMENT == 'dev':
    DEBUG = True
    SECRET_KEY = 'asdf'
    ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = []

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'emojiclock.urls'

WSGI_APPLICATION = 'emojiclock.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = False

USE_L10N = False

USE_TZ = True