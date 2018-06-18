"""
Django settings for interactions project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*ecns9a2uv0fbpd23qa0%usdjz_nfijld=giqxa5nfqr6ir@om'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'nested_admin',
    'admin_reorder',
    'interactionscore',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'interactions.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'interactions.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Custom user mode
# https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = 'interactionscore.User'


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    # the max interval you need to refresh the token at:
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=14),
    # when will the token expire even if refreshed in the meantime:
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=14),
}


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# admin settings
ADMIN_REORDER = (
    # Keep original label and models
    'sites',

    {'app': 'interactionscore', 'label': 'Core',
     'models': (
         'interactionscore.AffiliateGroup',
         'interactionscore.EngagementPlan',
     )},


    # # Reorder app models
    # {'app': 'orders', 'models': ('orders.Order', 'orders.PrinterOrder')},
    #
    # # models with custom name
    # {'app': 'interactionscore', 'label': 'Merchants', 'models': (
    #     {'model': 'interactionscore.Shop', 'label': 'Merchants'},
    # )},
    # # Exclude models
    # {'app': 'products', 'label': 'Templates', 'models': ('products.ProductTemplate',)},
    # {'app': 'products', 'label': 'Products', 'models': ('products.BrandedProduct',)},

    # Cross-linked models
    {'app': 'auth', 'models': ('interactionscore.User', 'auth.Group', 'auth.Permission')},

)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 'root': {
    #     'level': 'WARNING',
    #     'handlers': [
    #         'sentry',
    #     ],
    # },
    'root': {
        'level': 'WARNING',
        'handlers': [
            'all_log_file',
            'err_log_file',
        ],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'debug_log_file': {  # for temporary use while debugging
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/data/sysop/logs/interactions/debug.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'all_log_file': {  # complete log
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/data/sysop/logs/interactions/all.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'err_log_file': {  # errors log
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/data/sysop/logs/interactions/error.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
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
                'all_log_file',
                'err_log_file',
            ],
            'level': 'INFO',
            'propagate': True,
        },
        'debug': {
            'handlers': [
                'debug_log_file',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
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

from local_settings import *
