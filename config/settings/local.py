from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# In local dev we keep INFO logging but also show debug
LOGGING["root"]["level"] = "INFO"  # noqa: F405
