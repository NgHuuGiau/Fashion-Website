import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.test_settings_sqlite'
os.environ['SQLITE_TEST_DB'] = r'D:\Project\Fashion-Website\.tmp-e2e.sqlite3'
import django
django.setup()
from django.conf import settings
print('DB NAME:', settings.DATABASES['default']['NAME'])
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
