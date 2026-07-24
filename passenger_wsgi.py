import os
import sys

# Add project directory to path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'land_selling.settings')

# Set production defaults for cPanel
os.environ.setdefault('DJANGO_DEBUG', 'False')
os.environ.setdefault('DJANGO_SECRET_KEY', 'django-insecure-ndm=@ie_a+l=g#2t%p1d#h3gi3etn6gt@)0spt_es@88398x!7')
os.environ.setdefault('DB_NAME', 'wlsihszp_primelands')
os.environ.setdefault('DB_USER', 'wlsihszp_primelands')
os.environ.setdefault('DB_PASSWORD', 'Me32323383#&')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '3306')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
