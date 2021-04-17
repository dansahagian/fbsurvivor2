import os

from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOMAIN = config("DOMAIN", default="http://127.0.0.1:8000")
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="abcdefghijklmnop")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ["fbsurvivor.com"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

if DEBUG:
    ALLOWED_HOSTS = ["127.0.0.1"]
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

INTERNAL_IPS = ["127.0.0.1"]

CONTACT = config("CONTACT", default="")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_celery_beat",
    "fbsurvivor.core",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fbsurvivor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "fbsurvivor.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DATABASE"),
        "USER": config("PG_USER"),
        "PASSWORD": config("PG_PASSWORD"),
        "HOST": config("PG_HOST", default="127.0.0.1"),
        "PORT": config("PG_PORT", default=5423),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 15

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

HTML_MINIFY = True
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_URL = "/static/"
STATIC_ROOT = "/srv/www/static/"

SMTP_SERVER = config("SMTP_SERVER", default="")
SMTP_SENDER = config("SMTP_SENDER", default="")
SMTP_USER = config("SMTP_USER", default="")
SMTP_PASSWORD = config("SMTP_PASSWORD", default="")
SMTP_PORT = config("SMTP_PORT", default="")

TWILIO_SID = config("TWILIO_SID", default="")
TWILIO_KEY = config("TWILIO_KEY", default="")
TWILIO_NUM = config("TWILIO_NUM", default="")


# CELERY
BROKER_URL = config("BROKER_URL", default="amqp://localhost")
CELERY_TIMEZONE = "America/Los_Angeles"
