"""
Configuración para testing (CI/CD).
"""

from .base import *

DEBUG = False

# Base de datos en memoria para tests rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Hashers rápidos para tests
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Email en memoria para tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Media root temporal para tests
MEDIA_ROOT = '/tmp/test_media'

# Deshabilitar migraciones para tests más rápidos (opcional)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()