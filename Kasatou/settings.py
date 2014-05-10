"""
Django settings for Kasatou project.
"""

import os
BASE_DIR = "/home/sena/Devel/Kasatou"

SECRET_KEY = '3%dyqozgd4l)yheblv=-^lhbn1$js6uv5$7rh6r-qyi7gx88bf'

# TODO: Change this in production.
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INVITE_INITIAL_NUMBER_INVITATIONS = 3

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'invitation',  # invites.
    'Layers',  # boards.
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    BASE_DIR+'/templates',
)

STATICFILES_DIRS = (
    '/home/sena/Devel/Kasatou/static',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


ROOT_URLCONF = 'Kasatou.urls'

WSGI_APPLICATION = 'Kasatou.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static
STATIC_URL = '/static/'


# Media
MEDIA_ROOT = os.path.join(os.getcwd(), 'media')
MEDIA_URL = '/media/'


# Invites.
INVITE_MODE = True
INVITE_MODE_STRICT = True
ACCOUNT_INVITATION_DAYS = 3
INVITATIONS_PER_USER = 3

