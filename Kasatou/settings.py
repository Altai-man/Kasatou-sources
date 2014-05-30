"""
Django settings for Kasatou project.
"""
import os


#ON_OPENSHIFT = False
#if os.environ.has_key('OPENSHIFT_REPO_DIR'):
#    ON_OPENSHIFT = True


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '%dyqozgd4l)yheblv=-^lhbn1$js6uv5$7rh6r-qyi7gx88bf'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'database.db'),  # Or path to database file if using sqlite3.
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'wsgi', 'static')
STATIC_ROOT = os.path.join(os.getcwd(), 'Layers', 'static')


STATICFILES_FINDERS = ( 
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# Media
#MEDIA_ROOT = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'media')
MEDIA_ROOT = os.path.join(os.getcwd(),'media')
MEDIA_URL = '/media/'
