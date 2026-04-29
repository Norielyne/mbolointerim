from pathlib import Path
import os
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1ut@lnz#chaov$%!*^7y*g_6m3i$pak$g!kh*^*sff71%=a-93'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# --- CONFIGURATION RÉSEAU LOCAL ---
# On n'autorise que ton propre ordinateur
# Autorise tout le monde pour le test
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'norielyne.pythonanywhere.com','mbolointerim.onrender.com','whitenoise.middleware.WhiteNoiseMiddleware']

# On prévoit l'adresse que tu vas créer juste après
CSRF_TRUSTED_ORIGINS = [
    'https://mbolo-test-gabon.loca.lt',
    'http://mbolo-test-gabon.loca.lt',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'interim', # Ton application
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mbolo_project.urls'

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
                'interim.context_processors.notifications_messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'mbolo_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- CONFIGURATION GABON ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Libreville'
USE_I18N = True
USE_TZ = True

# --- FICHIERS STATIQUES ET MÉDIAS ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# STATIC_ROOT est nécessaire pour la production plus tard
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- AUTHENTIFICATION PERSONNALISÉE ---
AUTH_USER_MODEL = 'interim.User'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# --- RÉGLAGES SÉCURITÉ DES COOKIES (MODE LOCAL) ---
# TRÈS IMPORTANT : En local (HTTP), ces valeurs doivent être False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# On utilise 'Lax' pour les cookies en local
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# --- CONFIGURATION EMAIL ---


# --- CONFIGURATION EMAIL ---

# TRÈS IMPORTANT : Cette ligne doit pointer vers ton fichier de secours
EMAIL_BACKEND = 'custom_email_backend.CustomEmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# Utilise la même adresse partout pour éviter les blocages
EMAIL_HOST_USER = 'norilinedelarue5@gmail.com'
DEFAULT_FROM_EMAIL = 'Mbolo Intérim <norilinedelarue5@gmail.com>'

# Ton code d'application Google (16 caractères sans espaces)
EMAIL_HOST_PASSWORD = 'gxjkjcfvwqjjcfbs'

EMAIL_TIMEOUT = 10

# Reste de la config
SITE_ID = 1
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
logging.basicConfig(level=logging.DEBUG)
SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'