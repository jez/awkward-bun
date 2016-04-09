
from __future__ import print_function

import settings

def log(*args, **kwargs):
    if settings.DEBUG:
        print(*args, **kwargs)
