"""
WSGI config for chadbot_web project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chadbot_web.settings')

application = get_wsgi_application() 