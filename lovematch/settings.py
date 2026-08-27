import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Try loading environ
try:
    import environ
    env = environ.Env(
        DEBUG=(bool, True),
        SECRET_KEY=(str, 'django-insecure-prod-lovematch-enterprise-key-replace-in-production-998877'),
        ALLOWED_HOSTS=(list, ['*']),
        SECURE_SSL_REDIRECT=(bool, False),
        SESSION_COOKIE_SECURE=(bool, False),
        CSRF_COOKIE_SECURE=(bool, False),
    )
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        environ.Env.read_env(str(env_file))
except ImportError:
    class DummyEnv:
        def __call__(self, key, default=None, cast=None):
            val = os.environ.get(key, default)
            if cast is bool and isinstance(val, str):
                return val.lower() in ('true', '1', 'yes')
            if cast is list and isinstance(val, str):
                return [x.strip() for x in val.split(',') if x.strip()]
            return val
        def db(self, default=None):
            return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
    env = DummyEnv()

# Core Security Settings
SECRET_KEY = env('SECRET_KEY', default='django-insecure-prod-lovematch-enterprise-key-replace-in-production-998877')
DEBUG = env('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=['*'], cast=list)

# Application definition
INSTALLED_APPS = [
    'daphne',  # Daphne must be before django.contrib.staticfiles for ASGI
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'channels',
    # Local apps
    'accounts.apps.AccountsConfig',
    'matching.apps.MatchingConfig',
    'chat.apps.ChatConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for production static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lovematch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'lovematch.wsgi.application'
ASGI_APPLICATION = 'lovematch.asgi.application'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Support DATABASE_URL if configured
db_url = os.environ.get('DATABASE_URL')
if db_url and hasattr(env, 'db'):
    try:
        DATABASES['default'] = env.db('DATABASE_URL')
    except Exception:
        pass

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Channels Layer (WebSockets)
REDIS_URL = os.environ.get('REDIS_URL')
USE_REDIS_CHANNELS = os.environ.get('USE_REDIS_CHANNELS', 'False').lower() in ('true', '1')

if USE_REDIS_CHANNELS and REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }
else:
    # High-performance In-Memory layer for dev/single-instance production
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File Upload limits (Max 5MB per photo)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Production Security Headers
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=True, cast=bool)

# Google Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
