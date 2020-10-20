from .base import *

DEBUG = False

INSTALLED_APPS += [
    'pg_copy',
]

MIDDLEWARE += [
]

try:
    from .local import *
except ImportError:
    pass
