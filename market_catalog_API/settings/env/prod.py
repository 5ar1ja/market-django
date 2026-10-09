# python imports
from decouple import config  # noqa: I001

# local imports
from settings.base import *


DEBUG = False

ALLOWED_HOSTS = [""]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}
