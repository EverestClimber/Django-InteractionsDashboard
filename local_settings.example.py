# This file is included by mai settings.py, and has the change to
# overwrite any settings set there, and to select what other settings
# files to include.

# API-keys, PASSWORDS and other security sensitive infos go here,
# as this file will be git-ignored!

# Settings local to a developer's machine should also go here

# This file can in turn include one of `interactions/settings_staging.py`
# or `interactions/settings_production.py`, at the beginning, allowing
# easy overwirding of what's in these.

from interactions.settings_staging import *

# ...here goes the fun stuff...

DEBUG = True

# because sometimes we need to generate absolute paths without a request object
BASE_URL = 'http://localhost:8000'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # DEV
    'rest_framework',
    'corsheaders',
    'nested_admin',
    'admin_reorder',
    'interactionscore',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'otskinter',
        'USER': 'otskinter',
        'PASSWORD': '...',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
            # this gets you in-memory sqlite for tests, which is fast
            'ENGINE': 'django.db.backends.sqlite3',
        }
    }
}

CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    '127.0.0.1:8000'
)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    # 'root': {
    #     'level': 'WARNING',
    #     'handlers': [
    #         'sentry',
    #     ],
    # },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        # 'api': {
        #     'format': '%(asctime)s %(process)d.%(thread)d %(message)s',
        # }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'debug_log_file': {  # for temporary use while debugging
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../logs/debug.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'all_log_file': {  # complete log
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../logs/all.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'err_log_file': {  # errors log
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../logs/error.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        # 'api_log_file': {  # log Shopify API calls
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '../logs/api.log',
        #     'maxBytes': 10 * 1024 * 1024,
        #     'backupCount': 10,
        #     'formatter': 'api',
        # },
        # sentry
        # 'sentry': {
        #     'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
        #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        #     'tags': {'custom-tag': 'x'},
        # },
    },
    'loggers': {
        'django': {
            'handlers': [
                # for regular dev:
                'console',
                # production-like behavior
                'all_log_file',
                'err_log_file',
            ],
            'level': 'INFO',
            'propagate': True,
        },
        'debug': {
            'handlers': [
                # for regular dev:
                'console',
                # production-like behavior
                'debug_log_file',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
        # 'api': {
        #     'handlers': [
        #         # for regular dev:
        #         'console',
        #         # production-like behavior
        #         'api_log_file',
        #     ],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'raven': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # 'sentry.errors': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
    }
}
