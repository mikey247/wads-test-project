from .base import *

DEBUG = False

try:
    from .local import *
except ImportError:
    pass

# Add any Production ONLY apps and middleware here

# INSTALLED_APPS += [
# ]

# MIDDLEWARE += [
# ]
