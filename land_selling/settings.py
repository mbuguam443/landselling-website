from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-ndm=@ie_a+l=g#2t%p1d#h3gi3etn6gt@)0spt_es@88398x!7')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://9cc3-102-205-50-218.ngrok-free.app,https://*.onrender.com').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third party
    'crispy_forms',
    'crispy_tailwind',
    'django_filters',
    'whitenoise.runserver_nostatic',

    # Local apps
    'apps.accounts',
    'apps.website',
    'apps.projects',
    'apps.plots',
    'apps.customers',
    'apps.sales',
    'apps.payments',
    'apps.documents',
    'apps.notifications',
    'apps.reports',
    'apps.dashboard',
    'apps.settings',
    'apps.subscriptions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.AuditLogMiddleware',
    'apps.accounts.middleware.ProfileCompletionMiddleware',
    'apps.accounts.middleware.VerificationRequiredMiddleware',
]

ROOT_URLCONF = 'land_selling.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.website.context_processors.website_settings',
                'apps.notifications.context_processors.unread_notifications',
            ],
            'libraries': {
                'currency_filters': 'apps.plots.templatetags.currency_filters',
            },
        },
    },
]

WSGI_APPLICATION = 'land_selling.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'website:home'

# Company settings defaults
COMPANY_NAME = 'Prime Lands Ltd'
COMPANY_TAGLINE = 'Your Trusted Real Estate Partner'
COMPANY_EMAIL = 'info@primelands.com'
COMPANY_PHONE = '+254 700 000 000'
COMPANY_ADDRESS = '99 Westlands Rd, Nairobi, Kenya'

# M-Pesa Daraja API — all overridable via environment variables
MPESA_BASE_URL = os.environ.get('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '0GPg2z14A6LmnOAEMmFUJDlz7yYxMQEQNavDRWCBaD8PGcNo')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'D5XAaxpsX6D830m3imcl165raamoralJZk4bh3dcRAzxN52Glc70iH29OMGvOzVu')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://9cc3-102-205-50-218.ngrok-free.app/payments/mpesa/callback/')
