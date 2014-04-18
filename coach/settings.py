# Django settings for coach project.
from __future__ import absolute_import

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
  ('Bastien Abadie', 'bastien.abadie@gmail.com'),
)

# Used to hide admin page in urls, in Prod only
ADMIN_BASE_URL = False

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'devel.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

import os
HOME = os.path.realpath('.')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = HOME + '/medias'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nq!g^hyy-_l!*apn3302^5(jwt$t-&amp;!fo4my*^u3j!zj7=if%r'

# Load template trough jinja
TEMPLATE_LOADERS = (
  'coach.jinja.Loader',
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
)

JINJA2_TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'coach.menu.add_pages',
  'coach.settings.load_constants',
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'coach.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'coach.wsgi.application'

TEMPLATE_DIRS = (
  HOME + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'run',
    'users',
    'club',
    'page',
    'plan',
    'south',
)

# For auto login on user create
AUTHENTICATION_BACKENDS = (
  'users.backends.EmailAuthBackend',
  'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL='users.Athlete'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'coach.run.garmin' : {
          'handlers' : ['console'],
          'level': 'DEBUG',
        },
    }
}

# Sessions settings
SESSION_COOKIE_NAME = 'runreport'
SESSION_COOKIE_AGE = 7776000 # 3 months in seconds

# Redirect urls
LOGIN_URL = '/user/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/user/logout'
LOGOUT_REDIRECT_URL = '/'

# Date & Hour of Auto send
REPORT_SEND_DAY = 0
REPORT_SEND_TIME = (20,00)
REPORT_START_DATE = (2013, 0) # Week 0 of 2013

# Gnu GPG settings
GPG_HOME=''
GPG_KEY=''
GPG_PASSPHRASE=''

# Garmin user data (json)
GARMIN_DIR=os.path.join(HOME, 'garmin_data')

# PIWIK stats
PIWIK_HOST = False
PIWIK_ID = False

# Celery broker
BROKER_URL = 'redis://'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'UTC'

# Celery Periodic tasks
from datetime import timedelta
from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
  'garmin-import-10-min': {
    'task': 'run.tasks.garmin_import',
    'schedule': timedelta(minutes=10),
  },
  'send-race-mail-every-day-at-9': {
    'task': 'run.tasks.race_mail',
    'schedule': crontab(hour=9, minute=0),
  },
}

# Import local settings, if any
try:
  from coach.local_settings import *
except ImportError, e:
  pass

# Apps in prod
if not DEBUG:
  INSTALLED_APPS = INSTALLED_APPS + ('raven.contrib.django.raven_compat',)

# Load some settings constants in the templates
def load_constants(request):
  from django.conf import settings
  keys = ['DEBUG', 'PIWIK_HOST', 'PIWIK_ID', ]
  return dict([(k, getattr(settings, k, None)) for k in keys])
