from pathlib import Path
import environ
import os

from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/


environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY", default="secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])


# Application definition

INSTALLED_APPS = [
    "authbroker_client",
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "supply_chains",
    "accounts",
    "healthcheck",
    "rest_framework",
    "rest_framework.authtoken",
    "reversion",
    "webpack_loader",
    "django.forms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.add_cache_control_header_middleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "reversion.middleware.RevisionMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        **env.db("DATABASE_URL"),
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "accounts.auth.CustomAuthbrokerBackend",
]

LOGIN_URL = reverse_lazy("authbroker_client:login")
LOGIN_REDIRECT_URL = reverse_lazy("index")
AUTH_USER_MODEL = "accounts.User"
AUTHBROKER_URL = env("AUTHBROKER_URL", default="")
AUTHBROKER_CLIENT_ID = env("AUTHBROKER_CLIENT_ID", default="")
AUTHBROKER_CLIENT_SECRET = env("AUTHBROKER_CLIENT_SECRET", default="")

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# webpack-stats file is generated at the top level of the project
WEBPACK_LOADER = {
    "DEFAULT": {
        "STATS_FILE": os.path.join(BASE_DIR, "../webpack-stats.json"),
    },
}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets/webpack_bundles"),
]

CHARFIELD_MAX_LENGTH = 250

# To address models.W042 - type of the primary key
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Enable HSTS
# To disable in a local development environment,
# set the SET_HSTS_HEADERS environment variable to a value that Python will evaulate as False, e.g.
# export SET_HSTS_HEADERS=''

# Set security related headers
SET_HSTS_HEADERS = env("SET_HSTS_HEADERS", default=True)
if SET_HSTS_HEADERS:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True

# Settings for CSRF and Session cookies
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=True)
CSRF_COOKIE_HTTPONLY = env('CSRF_COOKIE_HTTPONLY', default=True)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=True)
SESSION_COOKIE_AGE = env('SESSION_COOKIE_AGE', default=60 * 60 * 10)