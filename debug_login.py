import django, os, sys, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'land_selling.settings')
django.setup()

from django.test import Client
from django.urls import resolve, reverse
from django.conf import settings

print('=== Settings ===')
print('DEBUG: %s' % settings.DEBUG)
print('ALLOWED_HOSTS: %s' % settings.ALLOWED_HOSTS)
print('LOGIN_URL: %s' % settings.LOGIN_URL)
print('LOGIN_REDIRECT_URL: %s' % settings.LOGIN_REDIRECT_URL)
print('MIDDLEWARE:')
for m in settings.MIDDLEWARE:
    print('  - %s' % m)

print('')
print('=== Test Login ===')
client = Client()
try:
    r1 = client.get(reverse('accounts:login'))
    print('GET login: %d' % r1.status_code)
    if r1.status_code != 200:
        print('ERROR: %s' % r1.content[:500])
except Exception as e:
    print('GET login EXCEPTION: %s' % e)
    traceback.print_exc()

print('')
print('=== POST Login ===')
try:
    r2 = client.post(reverse('accounts:login'), {'username': 'admin', 'password': 'admin123'}, follow=True)
    print('POST login status: %d' % r2.status_code)
    print('Redirect chain: %s' % r2.redirect_chain)
    if r2.status_code != 200:
        print('ERROR content: %s' % r2.content[:1000])
    else:
        print('Final URL: %s' % r2.wsgi_request.path)
        content = r2.content.lower()
        has_dashboard = b'dashboard' in content or b'admin' in content
        print('Has dashboard/admin: %s' % has_dashboard)
except Exception as e:
    print('POST login EXCEPTION: %s' % e)
    traceback.print_exc()
