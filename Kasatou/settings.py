"""
Django settings for Kasatou project.
"""
import os


ON_OPENSHIFT = False
if 'OPENSHIFT_REPO_DIR' in os.environ:
    ON_OPENSHIFT = True


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'some-cool-pass-here'

if ON_OPENSHIFT:
    DEBUG = False
    TEMPLATE_DEBUG = False
else:
    DEBUG = True
    TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'Layers.User'

# Application definition

PIC_SIZE = 180.0

# Paths that user can go without session.
ALLOWED_PATHS = ['/login/', '/bunny/', '/closed/']


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Layers',  # boards.
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    BASE_DIR+'/templates',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Layers.middleware.Invitation',
)

ROOT_URLCONF = 'Kasatou.urls'

WSGI_APPLICATION = 'Kasatou.wsgi.application'


if 'OPENSHIFT_APP_NAME' in os.environ:
    DB_NAME = os.environ['OPENSHIFT_APP_NAME']
if 'OPENSHIFT_POSTGRESQL_DB_USERNAME' in os.environ:
    DB_USER = os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME']
if 'OPENSHIFT_POSTGRESQL_DB_PASSWORD' in os.environ:
    DB_PASSWD = os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD']
if 'OPENSHIFT_POSTGRESQL_DB_HOST' in os.environ:
    DB_HOST = os.environ['OPENSHIFT_POSTGRESQL_DB_HOST']
if 'OPENSHIFT_POSTGRESQL_DB_PORT' in os.environ:
    DB_PORT = os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']

if ON_OPENSHIFT:
    # os.environ['OPENSHIFT_DB_*'] variables can be used with databases created
    # with rhc app cartridge add (see /README in this git repo)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': DB_NAME,               # Or path to database file if using sqlite3.
            'USER': DB_USER,               # Not used with sqlite3.
            'PASSWORD': DB_PASSWD,         # Not used with sqlite3.
            'HOST': DB_HOST,               # Set to empty string for localhost. Not used with sqlite3.
            'PORT': DB_PORT,               # Set to empty string for default. Not used with sqlite3.
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.path.join(BASE_DIR, 'sqlite3.db'),  # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
    

# Land & time.
LANGUAGE_CODE = "en_US"
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static
if ON_OPENSHIFT:
    STATIC_ROOT = os.path.join(os.environ['OPENSHIFT_REPO_DIR'], 'wsgi', 'static')
else:
    STATIC_ROOT = os.path.join(os.getcwd(), 'Layers', 'static')

STATIC_URL = '/static/'

STATICFILES_FINDERS = ( 
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# Media
if ON_OPENSHIFT:
    MEDIA_ROOT = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'media')
else:
    MEDIA_ROOT = os.path.join(os.getcwd(), 'media')

MEDIA_URL = '/media/'
