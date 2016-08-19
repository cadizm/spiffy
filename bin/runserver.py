import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'spiffy.settings'

import django
django.setup()

from django.core import management
management.call_command('runserver', '127.0.0.1:8001')
