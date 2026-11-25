import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name):
    return [item.strip() for item in os.environ.get(name, '').split(',') if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent

# Render sets the RENDER environment variable automatically.
ON_RENDER = bool(os.environ.get('RENDER'))


# ==========================================================
# SECURITY
# ==========================================================

# Local default: DEBUG on. On Render the default is DEBUG off.
# Override either way with the DEBUG environment variable.
DEBUG = env_bool('DEBUG', default=not ON_RENDER)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-local-development-key-only'
    else:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY must be set when DEBUG is off.'
        )

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + env_list('ALLOWED_HOSTS')

RENDER_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

if DEBUG:
    ALLOWED_HOSTS += ['.ngrok-free.dev', '.ngrok-free.app']

CSRF_TRUSTED_ORIGINS = [
    f'https://{host}' for host in ALLOWED_HOSTS
    if host not in ('localhost', '127.0.0.1') and not host.startswith('.')
]
CSRF_TRUSTED_ORIGINS += [
    f'https://*{host}' for host in ALLOWED_HOSTS if host.startswith('.')
]


# ==========================================================
# APPLICATIONS
# ==========================================================

INSTALLED_APPS = [
    # 'shop' must come BEFORE django.contrib.admin so that
    # shop/templates/admin/base_site.html (the Nqoba admin theme) is used.
    'shop',

    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary',
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
# URLS / WSGI
# ==========================================================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


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
                # Makes WHATSAPP_NUMBER, CURRENCY, etc. available in templates
                'shop.context_processors.site_info',
            ],
        },
    },
]


# ==========================================================
# DATABASE
# ==========================================================

# Local: SQLite file.  Render: set DATABASE_URL (Render Postgres provides it
# when the database is connected to the web service).

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.environ.get('DATABASE_URL'):
    import dj_database_url

    DATABASES['default'] = dj_database_url.parse(
        os.environ['DATABASE_URL'],
        conn_max_age=600,
    )

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# ==========================================================
# PASSWORD VALIDATION
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==========================================================
# INTERNATIONALISATION
# ==========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Mbabane'
USE_I18N = True
USE_TZ = True


# ==========================================================
# STATIC AND MEDIA FILES
# ==========================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# If a template points at a static file that does not exist, skip that one
# file instead of crashing the whole page.
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

USE_CLOUDINARY = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if USE_CLOUDINARY
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# ==========================================================
# EMAIL
# ==========================================================
# Priority:
#   1. BREVO_API_KEY set   -> send through Brevo's web API (works on Render's
#                             free plan, which blocks normal SMTP ports).
#   2. EMAIL_HOST_USER set -> normal SMTP (works on your computer / paid hosts).
#   3. Neither             -> emails are printed in the terminal.

BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')

if BREVO_API_KEY:
    EMAIL_BACKEND = 'shop.email_backend.BrevoEmailBackend'
elif EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_TIMEOUT = 10
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    f'Nqoba Creative <{EMAIL_HOST_USER}>' if EMAIL_HOST_USER
    else 'Nqoba Creative <noreply@nqobacreative.com>',
)


# ==========================================================
# SESSIONS
# ==========================================================

SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False


# ==========================================================
# PRODUCTION SECURITY
# ==========================================================

# Render terminates HTTPS in front of Django and forwards this header.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # Start small. Raise to 31536000 (1 year) once HTTPS is confirmed working.
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '3600'))


# ==========================================================
# LOGGING (visible in Render's log viewer)
# ==========================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}


# ==========================================================
# NQOBA CREATIVE BUSINESS SETTINGS
# ==========================================================

COMPANY_NAME = 'Nqoba Creative'
COMPANY_TAGLINE = 'Ideas Into Impact'
CURRENCY = 'E'

# International format, digits only, used for wa.me links.
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '26878336238')

CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'shabalamancoba8@gmail.com')
CONTACT_PHONES = ['+268 7833 6238', '+268 7971 7729']

# Where "new order" and "new enquiry" alerts are sent.
ORDER_NOTIFY_EMAIL = os.environ.get('ORDER_NOTIFY_EMAIL', CONTACT_EMAIL)
