from .env import *
import os

from .celery import *

if os.environ.get('MODE') == 'DEV':
    from .dev import *
elif os.environ.get('MODE') == 'PROD':
    from .prod import *
else:
    from .local import *