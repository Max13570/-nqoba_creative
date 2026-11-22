
"""
Django settings for Nqoba Creative project.
Local development, Ngrok and Render deployment.
"""

import os
from pathlib import Path


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# SECURITY
# ==========================================================

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-development-key-change-before-production'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.ngrok-free.dev',
    '.ngrok-free.app',
    '.onrender.com',
]

# Allow all hosts during development if required
if DEBUG:
    ALLOWED_HOSTS += ['*']


CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.dev',
    'https://*.ngrok-free.app',
    'https://*.onrender.com',
]


# ==========================================================
# APPLICATIONS
# ==========================================================

INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary',

    # Nqoba Creative application
    'shop',
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==========================================================
# URL CONFIGURATION
# ==========================================================

ROOT_URLCONF = 'config.urls'


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ==========================================================
# WSGI
# ==========================================================

WSGI_APPLICATION = 'config.wsgi.application'


# ==========================================================
# DATABASE
# ==========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

# Prevent AutoField warnings and preserve existing database IDs.

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# ==========================================================
# PASSWORD VALIDATION
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },

    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },

    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },

    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# ==========================================================
# INTERNATIONALIZATION
# ==========================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Mbabane'

USE_I18N = True

USE_TZ = True


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.StaticFilesStorage'
)


# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==========================================================
# CLOUDINARY CONFIGURATION
# ==========================================================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),

    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),

    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}


# ==========================================================
# STORAGE CONFIGURATION
# ==========================================================

if os.environ.get('CLOUDINARY_CLOUD_NAME'):

    # Render / production storage

    STORAGES = {
        'default': {
            'BACKEND': (
                'cloudinary_storage.storage.MediaCloudinaryStorage'
            ),
        },

        'staticfiles': {
            'BACKEND': (
                'django.contrib.staticfiles.storage.StaticFilesStorage'
            ),
        },
    }

else:

    # Local computer storage

    STORAGES = {
        'default': {
            'BACKEND': (
                'django.core.files.storage.FileSystemStorage'
            ),
        },

        'staticfiles': {
            'BACKEND': (
                'django.contrib.staticfiles.storage.StaticFilesStorage'
            ),
        },
    }


# ==========================================================
# EMAIL CONFIGURATION
# ==========================================================

# Development: emails appear in your terminal.

EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend'
)

DEFAULT_FROM_EMAIL = 'Nqoba Creative <noreply@nqobacreative.com>'


# ==========================================================
# SESSION SETTINGS
# ==========================================================

SESSION_COOKIE_AGE = 1209600  # 2 weeks

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = False


# ==========================================================
# SECURITY SETTINGS FOR PRODUCTION
# ==========================================================

if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = 'DENY'


# ==========================================================
# NQOBA CREATIVE PROJECT SETTINGS
# ==========================================================

# Company timezone
TIME_ZONE = 'Africa/Mbabane'

# Default currency used by the website
CURRENCY = 'E'

# Company name
COMPANY_NAME = 'Nqoba Creative'

# Company tagline
COMPANY_TAGLINE = 'Ideas Into Impact'
