from pathlib import Path
import os

# Jalur root folder project
BASE_DIR = Path(__file__).resolve().parent.parent

# Kunci rahasia Django
SECRET_KEY = 'django-insecure-isi-dengan-kunci-aman'

# Mode debug (True untuk pengembangan)
DEBUG = True

ALLOWED_HOSTS = []

LOGIN_URL = 'admin-login'  # Nama URL view login Anda
LOGIN_REDIRECT_URL = 'admin-dashboard'  # Ini bisa menjadi fallbac
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Aplikasi yang digunakan dalam proyek
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrap4',           # untuk {% load bootstrap4 %} di HTML
    'perpustakaan',         # nama aplikasi utama kamu
]

# Middleware (jangan ubah kecuali perlu)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Root routing URL
ROOT_URLCONF = 'perpus.urls'

# Template HTML (aktifkan APP_DIRS + DIRS jika pakai templates/)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # bisa dikosongkan jika semua HTML di dalam app
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

WSGI_APPLICATION = 'perpus.wsgi.application'

# Database: SQLite (default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Nonaktifkan validator password sementara untuk pengujian
AUTH_PASSWORD_VALIDATORS = []

# Bahasa & Zona Waktu
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True
USE_TZ = True

# Static file: CSS, JS, gambar
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# File upload/media jika diperlukan
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# Tipe ID otomatis
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'