"""
WSGI config for antidrone project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antidrone.settings')

application = get_wsgi_application()
