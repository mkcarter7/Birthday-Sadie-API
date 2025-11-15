import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
try:
    from dotenv import load_dotenv  # type: ignore
    env_path = BASE_DIR / '.env'
    result = load_dotenv(env_path)  # Explicitly point to .env file
    if result:
        print(f"[SETTINGS] Successfully loaded .env from {env_path}")
    else:
        print(f"[SETTINGS] .env file not found at {env_path}")
except Exception as e:
    # python-dotenv not installed; env vars can still be provided by OS/host
    print(f"[SETTINGS] Error loading .env: {e}")
    pass


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-u&9pi^=v(*69x^^$bjk^vokl9(+#u&7+u16m%o)y19*(jc5@+m')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Heroku sets this automatically, but allow manual override
# Default to localhost for local development, but require ALLOWED_HOSTS to be set in production
ALLOWED_HOSTS_STR = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'birthdayapi',
]

# REMOVED: Old CORS_ORIGIN_WHITELIST syntax (conflicts with CORS_ALLOWED_ORIGINS)
# CORS_ORIGIN_WHITELIST = (
#     'http://localhost:3000',
#     'http://localhost:8000'
# )

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files on Heroku
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'birthday.urls'

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

WSGI_APPLICATION = 'birthday.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# Database configuration - use PostgreSQL on Heroku, SQLite for local development
if os.getenv('DATABASE_URL'):
    import dj_database_url  # type: ignore
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for serving static files on Heroku
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'birthday.authentication.FirebaseAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS settings
# Parse CORS origins from environment variable (comma-separated)
# Default to localhost for development, plus Vercel deployment URL
CORS_ORIGINS_STR = os.getenv(
    'CORS_ALLOWED_ORIGINS', 
    'http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,https://birthday-sadie-client.vercel.app'
)
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(',') if origin.strip()]

CORS_ALLOW_CREDENTIALS = True

# Explicitly allow Authorization header
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Media files settings
# Use absolute URL in production (Heroku), relative in development
if os.getenv('DATABASE_URL'):  # On Heroku, DATABASE_URL is set
    # Production: Use full Heroku URL for media files
    MEDIA_URL = f'https://{os.getenv("ALLOWED_HOSTS", "").split(",")[0].strip()}/media/' if os.getenv('ALLOWED_HOSTS') else '/media/'
else:
    # Development: Use relative URL
    MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
