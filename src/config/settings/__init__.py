from .base import *
from os import getenv


PRODUCTION = int(getenv('PRODUCTION', 0))

if PRODUCTION:
    from .production import *
else:
    from .development import *