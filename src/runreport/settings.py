# Django settings for runreport project.
from __future__ import absolute_import

DEBUG = True

ADMINS = (
    ('Bastien Abadie', 'bastien@runreport.fr'),
)

# Used to hide admin page in urls, in Prod only
ADMIN_BASE_URL = False

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'runreport',
        'USER': 'runreport',
        'PASSWORD': 'runreport',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.realpath(os.path.join(BASE_DIR, '..'))


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# French locale
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Available languages for translations
from django.utils.translation import ugettext_lazy as _
LANGUAGES = (
    ('fr', _('French')),
    ('en', _('English')),
)

# Use our own locales
LOCALE_PATHS = (
    os.path.join(ROOT, '/locale'),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(ROOT, 'medias')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = '/medias/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT, 'static')

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(ROOT, 'front'),
)

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(ROOT, 'front/webpack-stats.json'),
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nq!g^hyy-_l!*apn3302^5(jwt$t-&amp;!fo4my*^u3j!zj7=if%r'


TEMPLATES = [
    # Django templates for apps
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(ROOT, 'templates_admin'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        }
    },

    # Jinja for our templates
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(ROOT, 'templates'),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'environment': 'runreport.jinja.environment',
            'extensions': [
                'jinja2.ext.i18n',
                'jinja2.ext.with_',
                'jinja2.ext.autoescape',
                'django_jinja.builtins.extensions.CsrfExtension',
                'django_jinja.builtins.extensions.UrlsExtension',
                'django_jinja.builtins.extensions.StaticFilesExtension',
                'django_jinja.builtins.extensions.DjangoFiltersExtension',
                'webpack_loader.contrib.jinja2ext.WebpackExtension',
            ],
        },
    },
]


MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'runreport.csrf.SubDomainCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'runreport.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'runreport.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'sport',
    'users',
    'club',
    'page',
    'plan',
    'messages',
    'tracks',
    'friends',
    'events',
    'post',
    'webpack_loader',
    'api',  # Api code
    'payments',  # Payments app
    'badges',  # Badges app
    'gear',  # Manage your gear
    'corsheaders',  # CORS for api
    #'vinaigrette', # Model translations
    'rest_framework',  # Api provider
    'django_countries',  # Countries selection
)

# For auto login on user create
AUTH_USER_MODEL = 'users.Athlete'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


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
        'console': {
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
        'runreport.sport.garmin': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'sport': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'club': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'payments': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

# Sessions settings
SESSION_COOKIE_NAME = 'runreport'
SESSION_COOKIE_AGE = 7776000  # 3 months in seconds

# Csrf cookie settings
CSRF_COOKIE_NAME = 'runreport.dev.csrf'

# Redirect urls
LOGIN_URL = '/user/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/user/logout'
LOGOUT_REDIRECT_URL = '/'

# Date & Hour of Auto send
REPORT_SEND_DAY = 0
REPORT_SEND_TIME = (20, 00)

# Gnu GPG settings
GPG_HOME = ''
GPG_KEY = ''
GPG_PASSPHRASE = ''

# Tracks data
TRACK_DATA = os.path.join(ROOT, 'tracks_data')

# Strava config
STRAVA_ID = 0
STRAVA_SECRET = ''

# Google Calendar
GCAL_CLIENT_ID = ''
GCAL_CLIENT_SECRET = ''

# Club Invite sender username
CLUB_INVITE_SENDER = 'sender'

# PIWIK stats
PIWIK_HOST = False
PIWIK_ID = False

# Facebook app credentials
FACEBOOK_ID = None
FACEBOOK_SECRET = None

# Celery broker
CELERY_ACCEPT_CONTENT = ('json', 'pickle')
CELERY_TASK_SERIALIZER = 'pickle'  # retro compat
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Europe/Paris'

# Celery Periodic tasks
from datetime import timedelta
from celery.schedules import crontab
CELERY_TASK_DEFAULT_QUEUE = 'base'
CELERY_TASK_IGNORE_RESULT = True
CELERY_BEAT_SCHEDULE = {
    'auto-send-reports-on-sunday': {
        'task': 'sport.tasks.auto_publish_reports',
        'schedule': crontab(day_of_week=0, hour=23, minute=0),
    },
    'tracks-import-10-min': {
        'task': 'tracks.tasks.tracks_import',
        'schedule': timedelta(minutes=30),
    },
    'send-race-mail-every-day-at-9': {
        'task': 'sport.tasks.race_mail',
        'schedule': crontab(hour=9, minute=10),
    },
    'build-demos-every-day-at-1am': {
        'task': 'users.tasks.build_demos',
        'schedule': crontab(hour=1, minute=0),
    },
    'send-sessions-report-every-morning': {
        'task': 'plan.tasks.athletes_daily_sessions',
        'schedule': crontab(hour=7, minute=30),
    },
    'send-related-races-every-morning': {
        'task': 'users.tasks.send_related_races_mail',
        'schedule': crontab(hour=7, minute=50),
    },
    'payment-status-every-morning': {
        'task': 'payments.tasks.auto_payments',
        'schedule': crontab(hour=9, minute=0),
    },
}
CELERY_TASK_ROUTES = {
    'tracks.tasks.provider_import': {
        'queue': 'tracks',
    },
}

# Retry celery failed tasks
CELERY_TASK_PUBLISH_RETRY = True
CELERY_TASK_PUBLISH_RETRY_POLICY = {
    'max_retries': 5,
    'interval_start': 0.1,
    'interval_step': 0.2,
    'interval_max': 0.5,
}


# Dev cache in files
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(ROOT, 'cache'),
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Test Engine
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Mailman 3.0 api
MAILMAN_URL = None
MAILMAN_DOMAIN = None
MAILMAN_USER = None
MAILMAN_PASS = None

# Help pages
HELP_URL = 'https://help.runreport.fr'

# API Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # Only auth using existing session
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # Only authenticated users access the api
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Allow cors api server
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'localhost:8100',
)

# Club creation is allowed directly
# No invite needed
CLUB_CREATION_OPEN = True

# Payments integration
PAYMENTS_ENABLED = False
PAYMENTS_AUTO = False
PAYMENTS_PERIOD = 30  # In days
MANGOPAY_ID = None
MANGOPAY_SECRET = None
MANGOPAY_PROD = False
MANGOPAY_CACHE = os.path.join(ROOT, '.mangopay')
MANGOPAY_ENTRY_FEE = 5.00  # in euros
MANGOPAY_RETURN_URL = 'http://localhost:8000'
MANGOPAY_NOTIFICATION_URL = 'http://localhost:8000'

# Archives dir
ARCHIVES_DIR = os.path.join(ROOT, 'archives')

# Premium prices, per month
PREMIUM_PRICES = {
    'athlete': 1.0,
    'trainer': 5.0,
    'staff': 1.0,
    'archive': 0.0,
}

# Plans url
PLANS_URL = 'https://plans.runreport.fr'

# Import local settings, if any
try:
    from runreport.local_settings import *
except ImportError as e:
    pass

# Apps in prod or dev
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
        DEBUG_TOOLBAR_CONFIG = {
            'JQUERY_URL': '',
        }
    except BaseException:
        print("Missing debug toolbar module")
else:
    # Add raven
    INSTALLED_APPS = INSTALLED_APPS + ('raven.contrib.django.raven_compat',)

    # Disable admin interface
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer', )

    # Secure csrf
    CSRF_COOKIE_SECURE = True


# Define Version
VERSION = '1.0'
