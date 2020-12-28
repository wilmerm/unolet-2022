"""
Archivo de configuración para localhost.

"""

from .base import *


NAME = "localhost"

# SECRET_KEY = 

DEBUG = True

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = MEDIA_ROOT / NAME

SITE_ID = 1