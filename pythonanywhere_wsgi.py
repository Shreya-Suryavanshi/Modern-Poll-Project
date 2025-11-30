"""
WSGI config for PythonAnywhere deployment
"""
import os
import sys
from pathlib import Path

# Add your project directory to the sys.path
project_home = '/home/shreya-suryavanshi/poll_project'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poll_project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
